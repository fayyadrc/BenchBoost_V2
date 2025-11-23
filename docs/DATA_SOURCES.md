# FPL Data Sources & Formats

This document provides a comprehensive overview of all data sources available in this FPL application, including API endpoints and scraped data, along with their data structures and formats.

---

## Table of Contents
- [Core Data Cache](#core-data-cache)
- [API Data Sources](#api-data-sources)
- [Scraped Data Sources](#scraped-data-sources)
- [Helper Functions](#helper-functions)

---

## Core Data Cache

The application maintains a module-level cache (`core_data`) that organizes FPL data for quick access.

### Structure

```python
core_data = {
    "players": {},           # player_id -> player details
    "teams": {},             # team_id -> team details
    "gameweeks": {},         # gameweek_id -> gameweek details
    "fixtures": {},          # fixture_id -> fixture details
    "players_by_name": {},   # player_name (lowercase) -> player details
    "teams_by_name": {},     # team_name/short_name (lowercase) -> team details
    "bootstrap_static": {},  # Full bootstrap-static response
    "game_settings": {}      # Game settings from bootstrap
}
```

### Loaded by: `load_core_game_data()`
**Note**: Automatically filters out transferred players (status='u')

---

## API Data Sources

### 1. Bootstrap Static
**Function**: `bootstrap_static()`  
**Endpoint**: `https://fantasy.premierleague.com/api/bootstrap-static/`  
**Authentication**: Not required

#### Returns
```json
{
  "events": [...],           // Array of gameweek objects
  "teams": [...],            // Array of team objects
  "elements": [...],         // Array of player objects
  "element_types": [...],    // Position types (GK, DEF, MID, FWD)
  "element_stats": [...],    // Available stat categories
  "game_settings": {...},    // Game rules and settings
  "phases": [...],           // Season phases
  "total_players": 12345678  // Total FPL managers
}
```

#### Player Object (Element) Fields
```json
{
  "id": 1,
  "web_name": "Haaland",
  "first_name": "Erling",
  "second_name": "Haaland",
  "team": 14,                    // Team ID
  "element_type": 4,             // Position (1=GK, 2=DEF, 3=MID, 4=FWD)
  "now_cost": 145,               // Price in tenths (14.5m)
  "total_points": 234,
  "points_per_game": "7.8",
  "minutes": 2430,
  "goals_scored": 28,
  "assists": 5,
  "clean_sheets": 12,
  "bonus": 25,
  "selected_by_percent": "45.3",
  "form": "8.2",
  "status": "a",                 // a=available, i=injured, d=doubtful, s=suspended, u=unavailable(transferred)
  "chance_of_playing_next_round": 100,
  "chance_of_playing_this_round": 100,
  "news": "",
  "news_added": null,
  "in_dreamteam": true,
  "dreamteam_count": 5,
  "yellow_cards": 3,
  "red_cards": 0,
  "saves": 0,
  "penalties_saved": 0,
  "penalties_missed": 1,
  "own_goals": 0,
  "influence": "1234.5",
  "creativity": "567.8",
  "threat": "1890.2",
  "ict_index": "123.4",
  "transfers_in": 1234567,
  "transfers_out": 234567,
  "transfers_in_event": 12345,
  "transfers_out_event": 2345
}
```

#### Team Object Fields
```json
{
  "id": 1,
  "name": "Arsenal",
  "short_name": "ARS",
  "code": 3,
  "strength": 4,
  "strength_overall_home": 1320,
  "strength_overall_away": 1280,
  "strength_attack_home": 1300,
  "strength_attack_away": 1260,
  "strength_defence_home": 1340,
  "strength_defence_away": 1300,
  "position": 2,
  "played": 15,
  "win": 10,
  "draw": 3,
  "loss": 2,
  "points": 33,
  "pulse_id": 1
}
```

#### Gameweek (Event) Object Fields
```json
{
  "id": 15,
  "name": "Gameweek 15",
  "deadline_time": "2025-11-30T11:30:00Z",
  "average_entry_score": 52,
  "finished": false,
  "data_checked": false,
  "highest_score": 124,
  "highest_scoring_entry": 1234567,
  "is_previous": false,
  "is_current": true,
  "is_next": false,
  "cup_leagues_created": false,
  "chip_plays": [...],
  "most_selected": 123,
  "most_transferred_in": 123,
  "most_captained": 123,
  "most_vice_captained": 123,
  "top_element": 123,
  "top_element_info": {...},
  "transfers_made": 12345678
}
```

---

### 2. Event Live
**Function**: `event_live(event_id)`  
**Endpoint**: `https://fantasy.premierleague.com/api/event/{event_id}/live/`  
**Authentication**: Not required

#### Returns
```json
{
  "elements": [
    {
      "id": 123,
      "stats": {
        "minutes": 90,
        "goals_scored": 2,
        "assists": 1,
        "clean_sheets": 0,
        "goals_conceded": 2,
        "own_goals": 0,
        "penalties_saved": 0,
        "penalties_missed": 0,
        "yellow_cards": 1,
        "red_cards": 0,
        "saves": 0,
        "bonus": 3,
        "bps": 67,
        "influence": "123.4",
        "creativity": "45.6",
        "threat": "89.2",
        "ict_index": "12.3",
        "total_points": 15,
        "in_dreamteam": true
      },
      "explain": [
        {
          "fixture": 123,
          "stats": [
            {
              "identifier": "goals_scored",
              "points": 10,
              "value": 2
            },
            {
              "identifier": "assists",
              "points": 3,
              "value": 1
            }
          ]
        }
      ]
    }
  ]
}
```

---

### 3. Fixtures
**Function**: `fixtures(event=None)`  
**Endpoint**: `https://fantasy.premierleague.com/api/fixtures/` or `?event={event_id}`  
**Authentication**: Not required

#### Returns (Array)
```json
[
  {
    "id": 123,
    "code": 123456,
    "event": 15,                    // Gameweek ID
    "finished": false,
    "finished_provisional": false,
    "kickoff_time": "2025-11-30T15:00:00Z",
    "minutes": 0,
    "provisional_start_time": false,
    "started": false,
    "team_a": 1,                    // Away team ID
    "team_a_score": null,
    "team_h": 14,                   // Home team ID
    "team_h_score": null,
    "team_h_difficulty": 4,
    "team_a_difficulty": 2,
    "pulse_id": 123456,
    "stats": []
  }
]
```

---

### 4. Entry Summary
**Function**: `entry_summary(entry_id)`  
**Endpoint**: `https://fantasy.premierleague.com/api/entry/{entry_id}/`  
**Authentication**: Not required (public info)

#### Returns
```json
{
  "id": 1605977,
  "joined_time": "2024-08-15T10:30:00Z",
  "started_event": 1,
  "favourite_team": 14,
  "player_first_name": "John",
  "player_last_name": "Doe",
  "player_region_id": 1,
  "player_region_name": "England",
  "player_region_iso_code_short": "ENG",
  "player_region_iso_code_long": "ENG",
  "summary_overall_points": 1234,
  "summary_overall_rank": 123456,
  "summary_event_points": 65,
  "summary_event_rank": 234567,
  "current_event": 15,
  "leagues": {
    "classic": [...],
    "h2h": [...]
  },
  "name": "Team Name",
  "name_change_blocked": false,
  "kit": {...},
  "last_deadline_bank": 25,       // Budget remaining (in tenths)
  "last_deadline_value": 1000,    // Squad value
  "last_deadline_total_transfers": 15
}
```

---

### 5. Entry History
**Function**: `entry_history(entry_id)`  
**Endpoint**: `https://fantasy.premierleague.com/api/entry/{entry_id}/history/`  
**Authentication**: Not required

#### Returns
```json
{
  "current": [                    // Current season GW-by-GW
    {
      "event": 1,
      "points": 67,
      "total_points": 67,
      "rank": 1234567,
      "rank_sort": 1234567,
      "overall_rank": 1234567,
      "bank": 5,                  // Budget remaining (in tenths)
      "value": 1000,              // Squad value
      "event_transfers": 0,
      "event_transfers_cost": 0,
      "points_on_bench": 15
    }
  ],
  "past": [                       // Previous seasons
    {
      "season_name": "2023/24",
      "total_points": 2345,
      "rank": 123456
    }
  ],
  "chips": [                      // Chips used this season
    {
      "name": "bboost",
      "time": "2025-01-01T11:30:00Z",
      "event": 19
    }
  ]
}
```

---

### 6. Gameweek Picks
**Function**: `gameweek_picks(entry_id, event_id, cookies)`  
**Endpoint**: `https://fantasy.premierleague.com/api/entry/{entry_id}/event/{event_id}/picks/`  
**Authentication**: Required (needs cookies for some entries)

#### Returns
```json
{
  "active_chip": null,            // or "bboost", "3xc", "wildcard", "freehit"
  "automatic_subs": [
    {
      "entry": 1605977,
      "element_in": 234,
      "element_out": 123,
      "event": 15
    }
  ],
  "entry_history": {
    "event": 15,
    "points": 65,
    "total_points": 1234,
    "rank": 123456,
    "rank_sort": 123456,
    "overall_rank": 234567,
    "bank": 5,
    "value": 1000,
    "event_transfers": 1,
    "event_transfers_cost": 4,
    "points_on_bench": 12
  },
  "picks": [
    {
      "element": 123,             // Player ID
      "position": 1,              // Position in team (1-15)
      "multiplier": 2,            // 2=captain, 3=triple captain, 0=benched
      "is_captain": true,
      "is_vice_captain": false
    }
  ]
}
```

---

### 7. Element Summary
**Function**: `element_summary(element_id)`  
**Endpoint**: `https://fantasy.premierleague.com/api/element-summary/{element_id}/`  
**Authentication**: Not required

#### Returns
```json
{
  "fixtures": [                   // Upcoming fixtures for player
    {
      "id": 123,
      "code": 123456,
      "team_h": 14,
      "team_h_score": null,
      "team_a": 1,
      "team_a_score": null,
      "event": 16,
      "finished": false,
      "minutes": 0,
      "provisional_start_time": false,
      "kickoff_time": "2025-12-07T15:00:00Z",
      "event_name": "Gameweek 16",
      "is_home": true,
      "difficulty": 4
    }
  ],
  "history": [                    // Past gameweek performances
    {
      "element": 123,
      "fixture": 456,
      "opponent_team": 1,
      "total_points": 12,
      "was_home": true,
      "kickoff_time": "2025-11-23T15:00:00Z",
      "team_h_score": 3,
      "team_a_score": 1,
      "round": 14,
      "minutes": 90,
      "goals_scored": 2,
      "assists": 1,
      "clean_sheets": 0,
      "goals_conceded": 1,
      "own_goals": 0,
      "penalties_saved": 0,
      "penalties_missed": 0,
      "yellow_cards": 0,
      "red_cards": 0,
      "saves": 0,
      "bonus": 3,
      "bps": 67,
      "influence": "123.4",
      "creativity": "45.6",
      "threat": "89.2",
      "ict_index": "12.3",
      "value": 145,
      "transfers_balance": 123456,
      "selected": 3456789,
      "transfers_in": 123456,
      "transfers_out": 78901
    }
  ],
  "history_past": [               // Performance in previous seasons
    {
      "season_name": "2023/24",
      "element_code": 123456,
      "start_cost": 105,
      "end_cost": 125,
      "total_points": 234,
      "minutes": 2890,
      "goals_scored": 23,
      "assists": 8,
      "clean_sheets": 12,
      "goals_conceded": 35,
      "own_goals": 0,
      "penalties_saved": 0,
      "penalties_missed": 2,
      "yellow_cards": 4,
      "red_cards": 0,
      "saves": 0,
      "bonus": 18,
      "bps": 789,
      "influence": "1234.5",
      "creativity": "567.8",
      "threat": "1890.2",
      "ict_index": "123.4"
    }
  ]
}
```

---

### 8. Transfers History
**Function**: `transfers_history(entry_id)`  
**Endpoint**: `https://fantasy.premierleague.com/api/entry/{entry_id}/transfers/`  
**Authentication**: Not required

#### Returns (Array)
```json
[
  {
    "element_in": 234,            // Player ID brought in
    "element_in_cost": 85,        // Cost in tenths
    "element_out": 123,           // Player ID transferred out
    "element_out_cost": 95,       // Cost in tenths
    "entry": 1605977,
    "event": 15,                  // Gameweek of transfer
    "time": "2025-11-29T10:30:00Z"
  }
]
```

---

### 9. League Standings
**Function**: `league_standings(league_id, page_standings, phase)`  
**Endpoint**: `https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/`  
**Authentication**: Not required for public leagues

#### Returns
```json
{
  "new_entries": {
    "has_next": false,
    "page": 1,
    "results": []
  },
  "last_updated_data": "2025-11-30T18:00:00Z",
  "league": {
    "id": 314,
    "name": "Overall",
    "created": "2024-08-01T00:00:00Z",
    "closed": false,
    "max_entries": null,
    "league_type": "x",
    "scoring": "c",
    "start_event": 1,
    "code_privacy": "p",
    "has_cup": false,
    "cup_league": null,
    "rank": null
  },
  "standings": {
    "has_next": true,
    "page": 1,
    "results": [
      {
        "id": 1234567,
        "event_total": 67,
        "player_name": "John Doe",
        "rank": 1,
        "last_rank": 2,
        "rank_sort": 1,
        "total": 1456,
        "entry": 1234567,
        "entry_name": "Team Name"
      }
    ]
  }
}
```

---

### 10. Authenticated Entry Details
**Function**: `entry_details(cookies)`  
**Endpoint**: `https://fantasy.premierleague.com/api/me/`  
**Authentication**: Required (needs cookies)

#### Returns
```json
{
  "player": {
    "date_of_birth": "1990-01-01",
    "dirty": false,
    "email": "user@example.com",
    "entry": 1605977,
    "first_name": "John",
    "gender": "m",
    "last_name": "Doe",
    "region": 1,
    "terms_and_conditions_accepted_version": "1.0"
  }
}
```

---

### 11. My Team
**Function**: `my_team(entry_id, cookies)`  
**Endpoint**: `https://fantasy.premierleague.com/api/my-team/{entry_id}/`  
**Authentication**: Required (needs cookies)

#### Returns
```json
{
  "picks": [
    {
      "element": 123,
      "position": 1,
      "selling_price": 145,
      "multiplier": 2,
      "purchase_price": 140,
      "is_captain": true,
      "is_vice_captain": false
    }
  ],
  "chips": [
    {
      "status_for_entry": "available",
      "played_by_entry": [],
      "name": "bboost",
      "number": 1,
      "start_event": 1,
      "stop_event": 38,
      "chip_type": "team"
    }
  ],
  "transfers": {
    "cost": 0,
    "status": "cost",
    "limit": null,
    "made": 0,
    "bank": 5,
    "value": 1000
  }
}
```

---

## Calculated Player Statistics

### Function: `get_all_players_with_stats()`

Returns enhanced player data with calculated statistics. **Note**: Automatically filters out transferred players.

#### Returns (Array)
```json
[
  {
    "id": 123,
    "name": "Haaland",
    "full_name": "Erling Haaland",
    "position": 4,                              // 1=GK, 2=DEF, 3=MID, 4=FWD
    "team": 14,
    "total_points": 234,
    "minutes_played": 2430,
    "cost": 14.5,                               // Converted from tenths
    "points_per_game": 7.8,
    "points_per_game_per_million": 0.54,       // PPG / cost
    "bonus_per_90": 0.93,                      // Bonus / appearances
    "points_per_90": 8.67,                     // Total points / appearances
    "points_per_million": 16.14,               // Total points / cost
    "points_per_million_per_90": 0.60,         // PPG per 90 / cost
    "assists": 5,
    "selected_by_percent": 45.3,
    "form": 8.2
  }
]
```

**Calculated Metrics Explained**:
- `points_per_game_per_million`: Value metric (higher = better value)
- `points_per_90`: Efficiency when playing (accounts for rotation)
- `points_per_million`: Season-long value
- `points_per_million_per_90`: Combined efficiency and value metric
- `bonus_per_90`: Bonus point consistency

---

## Scraped Data Sources

### Source: plan.livefpl.net

**Script**: `scrape.py`  
**Method**: Playwright (headless browser automation)  
**Authentication**: Not required (public data)

### Output Structure

```json
{
  "gameweek_summary": {
    "rank_direction": "up",              // "up", "down", or "unchanged"
    "status": "You rose",
    "arrow_type": "green",               // "green" or "red"
    "margin": "23,456 places",
    "gameweek_points": "67 pts",
    "safety_score": "78/100"
  },
  "captain": {
    "caption": "Haaland delivered",     // or "Haaland blanked"
    "result": "24 points"                // or "2 points"
  },
  "team_players": [
    {
      "name": "Haaland",
      "points": "24"                     // String format
    },
    {
      "name": "Saka",
      "points": "7"
    }
  ],
  "differentials": [
    {
      "name": "Palmer",
      "points": 12,
      "ownership": "23.4%"               // Ownership in your rank range
    }
  ],
  "threats": [
    {
      "name": "Salah",
      "points": 18,
      "ownership": "67.8%"               // Players you don't own, popular in your rank
    }
  ]
}
```

### Data Descriptions

#### Gameweek Summary
- **rank_direction**: Overall rank movement direction
- **status**: Text description of rank change
- **arrow_type**: Visual indicator color
- **margin**: Number of places moved
- **gameweek_points**: Points scored this GW
- **safety_score**: Risk/safety metric (0-100)

#### Captain Info
- **caption**: Performance description of captain choice
- **result**: Captain points (doubled)

#### Team Players
Individual performance of all 15 squad players for the gameweek

#### Differentials
Players you own that are less commonly owned in your rank bracket (potential rank risers)

#### Threats
Highly-owned players you don't have (potential rank fallers if they perform)

---

## Helper Functions

### Quick Lookup Functions

```python
# Get player by ID
get_player_by_id(player_id: int) -> Optional[Dict]

# Get player by name (case-insensitive)
get_player_by_name(player_name: str) -> Optional[Dict]

# Get team by ID
get_team_by_id(team_id: int) -> Optional[Dict]

# Get team by name (case-insensitive, matches full name or short name)
get_team_by_name(team_name: str) -> Optional[Dict]

# Get gameweek by ID
get_gameweek_by_id(gameweek_id: int) -> Optional[Dict]

# Get current active gameweek
get_current_gameweek() -> Optional[Dict]

# Get fixture by ID
get_fixture_by_id(fixture_id: int) -> Optional[Dict]
```

### Usage Examples

```python
# Load all core data once
load_core_game_data()

# Quick lookups (no API calls)
haaland = get_player_by_name("Haaland")
arsenal = get_team_by_name("ARS")  # or "Arsenal"
current_gw = get_current_gameweek()

# Get enhanced player statistics
top_players = get_all_players_with_stats()
```

---

## Position Types

| ID | Position | Short Code |
|----|----------|------------|
| 1  | Goalkeeper | GK |
| 2  | Defender | DEF |
| 3  | Midfielder | MID |
| 4  | Forward | FWD |

---

## Player Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `a` | Available | Fit and available for selection |
| `d` | Doubtful | 50% chance of playing |
| `i` | Injured | Currently injured |
| `s` | Suspended | Currently suspended |
| `u` | Unavailable | Transferred out of Premier League |
| `n` | Not in squad | Dropped from squad |

**Note**: Players with status `u` are filtered out of most data functions as they're no longer FPL assets.

---

## Data Refresh Recommendations

### Real-time Data (refresh frequently)
- Event live data
- Gameweek picks (during live GW)
- Fixtures (for score updates)

### Daily Updates
- Bootstrap static (player prices, ownership changes)
- Entry summary and history
- League standings

### Weekly Updates
- Element summary (before deadline)
- Transfers history
- Scraped differential/threat data

### Season Updates
- Past season history (once per season)

---

## Error Handling

All API functions raise `requests.HTTPError` on failed requests with response content for debugging.

```python
try:
    data = bootstrap_static()
except requests.HTTPError as e:
    print(f"API Error: {e}")
```

Scraped data may contain `"error"` fields in objects when extraction fails:
```json
{
  "name": "Error",
  "points": 0,
  "ownership": "0%",
  "error": "Element not found"
}
```

---

## Authentication

Some endpoints require FPL login cookies:
- `my_team()`
- `entry_details()`
- `gameweek_picks()` (for private entries)

To obtain cookies, log into the FPL website and extract session cookies from your browser.

---

## Rate Limiting

The FPL API does not publish official rate limits, but recommended best practices:
- Use `requests.Session()` for connection pooling
- Cache bootstrap-static data (changes infrequently)
- Avoid parallel requests to the same endpoint
- Implement exponential backoff on errors

---

## Additional Resources

- Official FPL Website: https://fantasy.premierleague.com/
- Live FPL: https://www.livefpl.net/
- FPL Plan: https://plan.livefpl.net/

# Data Sources & Available Data Summary

## Official FPL API
*   **General Game Data**: 
    *   Players (elements): Price, position, ownership, status.
    *   Teams: Name, short name, strength.
    *   Gameweeks (events): Deadlines, average scores, highest scores.
    *   Game Settings: Rules, chip definitions.
*   **Live Scoring**: 
    *   Real-time points for the current gameweek.
    *   Match stats: Goals, assists, bonus points, saves, cards.
*   **Manager Data**: 
    *   Team history and past performance.
    *   Current gameweek picks and substitutes.
    *   Transfer history and chip usage.
*   **Fixtures**: 
    *   Match schedule and results.
    *   Fixture difficulty ratings (FDR).

## FPL Alerts (Scraped)
*   **Price Changes**: Real-time player price rises and falls.
*   **Status Updates**: News on injuries, suspensions, and availability.
*   **Market Activity**: Trends in player transfers (in/out).

## LiveFPL (Scraped)
*   **Live Rank**: Real-time overall rank estimation and rank movement (green/red arrows).
*   **Team Analysis**: 
    *   **Differentials**: Low-ownership players in your team.
    *   **Threats**: High-ownership players not in your team.
*   **Captaincy**: Captain points and effective ownership stats.
*   **Chip Usage**: Active chips for the current gameweek.

## FBref (Scraped)
*   **Advanced Stats**: 
    *   Expected Goals (xG) and Expected Assists (xA).
    *   Shot creating actions, progressive carries.
*   **Performance Metrics**: Shots, passes, tackles, blocks, interceptions.
*   **Playing Time**: Matches played, starts, minutes per game.

## Local Data
*   **Player Stats JSON**: Cached collection of player statistics (`pl_player_stats.json`).



## VECTOR DB

* Player metadata (name, team, position)

* Player biography / long-term profiles

* Team names and strengths (if static)

* Game settings & chip definitions

* Season fixture list

* Static FDR

* FBref all stats (xG, xA, SCA, carries, defensive stats)

* Historical performance summaries

* Local cached player stats JSON

* Structural LiveFPL concepts (not numbers)

## LIVE FETCH

* Current player status (injured/flags)

* Price changes / predictions

* Transfer trends (in/out this GW)

* Selected-by-%

Real-time match events

Player points (GW + Total)

Manager picks & transfer history

Chip usage this GW

Live rank (LiveFPL)

Effective ownership (EO)

Live captain points

Fixture results

Dynamic fixture difficulty (if recalculated)*