# 📚 FPL Data Sources & Architecture

This document outlines the data architecture for the BenchBoost FPL Chatbot, detailing where data comes from, how it is stored, and how it is accessed.

---

## 🏗️ Architecture Overview

The application uses a hybrid data approach:
1.  **MongoDB**: Acts as the persistent store for static data (Teams, Players, Fixtures).
2.  **FPL API**: The primary source of truth, accessed directly for real-time user data (My Team, Live Points).
3.  **Web Scrapers**: Gathers supplementary data (Price Changes, Live Rank) not easily available via the official API.
4.  **In-Memory Cache**: Loads core game data at startup for fast access by the chatbot agent.

---

## 🗄️ Primary Database (MongoDB)

**Connection**: Managed via `backend/database/db.py` using `pymongo`.
**Ingestion**: Run via `backend/database/ingestion.py`.

### Collections

#### 1. `teams`
Static data for all 20 Premier League clubs.
- **Source**: FPL API (`bootstrap-static`)
- **Key Fields**:
  - `id`: Unique Team ID (e.g., 1)
  - `name`: Full Name (e.g., "Arsenal")
  - `short_name`: Abbreviation (e.g., "ARS")
  - `strength`: Overall strength rating (1-5)

#### 2. `players`
Comprehensive data for all active players.
- **Source**: FPL API (`bootstrap-static`)
- **Key Fields**:
  - `id`: Unique Player ID
  - `web_name`: Display Name (e.g., "Haaland")
  - `team`: Team ID
  - `element_type`: Position (1=GKP, 2=DEF, 3=MID, 4=FWD)
  - `now_cost`: Current Price (e.g., 140 = £14.0m)
  - `status`: Availability (`a`=Available, `i`=Injured, `d`=Doubtful, `s`=Suspended)
  - `_last_updated`: Timestamp of last ingestion

#### 3. `gameweeks`
Schedule and status of the season's 38 gameweeks.
- **Source**: FPL API (`bootstrap-static`)
- **Key Fields**:
  - `id`: Gameweek ID (1-38)
  - `deadline_time`: ISO Timestamp
  - `is_current`: Boolean (True if active GW)
  - `is_next`: Boolean (True if upcoming GW)

#### 4. `fixtures`
Match schedule and results.
- **Source**: FPL API (`fixtures`)
- **Key Fields**:
  - `id`: Fixture ID
  - `event`: Gameweek ID
  - `team_h`: Home Team ID
  - `team_a`: Away Team ID
  - `kickoff_time`: ISO Timestamp
  - `finished`: Boolean

---

## 🌐 External APIs (FPL)

The application interacts with the official Fantasy Premier League API.
**Client**: `backend/data/api_client.py`

| Function | Endpoint | Description | Auth Required |
|----------|----------|-------------|---------------|
| `bootstrap_static` | `/bootstrap-static/` | Core game data (players, teams, events) | ❌ |
| `fixtures` | `/fixtures/` | Match schedule and results | ❌ |
| `element_summary` | `/element-summary/{id}/` | Player history and upcoming fixtures | ❌ |
| `entry_summary` | `/entry/{id}/` | Manager details and overall rank | ❌ |
| `entry_history` | `/entry/{id}/history/` | Manager season history | ❌ |
| `my_team` | `/my-team/{id}/` | Current squad and chips (requires login) | ✅ |
| `gameweek_picks` | `/entry/{id}/event/{gw}/picks/` | Manager's team for a specific GW | ✅ |

---

## 🕷️ Scraped Data Sources

Supplementary data gathered via web scraping (Playwright/Selenium).

### 1. Live Rank & Differentials
**Source**: [LiveFPL](https://plan.livefpl.net)
**Script**: `backend/data/livefpl_scrape.py`
**Data Points**:
- **Live Rank**: Real-time rank updates during matches.
- **Differentials**: Low-owned players in your squad who can boost your rank.
- **Threats**: High-owned players you don't own who threaten your rank.
- **Safety Score**: A metric indicating how "safe" your rank is.

### 2. Price Changes & News
**Source**: [FPL Alerts](https://www.fplalerts.com/videprinter/)
**Script**: `backend/data/fplNews_scrape.py`
**Data Points**:
- **Price Rises/Falls**: Real-time player price changes.
- **Status Updates**: Injury news and press conference updates.

---

## ⚡ In-Memory Cache

To reduce API latency, the chatbot loads core data into memory at startup.
**Module**: `backend/data/cache.py`

**Cached Data**:
- `players`: Dict mapping ID -> Player Object
- `players_by_name`: Dict mapping Name -> Player Object (for fast lookup)
- `teams`: Dict mapping ID -> Team Object
- `gameweeks`: Dict mapping ID -> Gameweek Object
- `fixtures`: Dict mapping ID -> Fixture Object

**Note**: The cache is populated directly from the FPL API (`bootstrap_static`) on startup, ensuring the chatbot always has the latest data session.