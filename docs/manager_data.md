# FPL API Documentation

This documentation provides a comprehensive guide to the publicly available endpoints for the Fantasy Premier League (FPL) API. It covers how to access data regarding fixtures, teams, managers, leagues, and more.

**Base URL:** `https://fantasy.premierleague.com/api/`

> **Note:** These APIs have a CORS policy, meaning they cannot be called directly from a front-end client (browser) without a proxy.

## Table of Contents
- [Getting Started](#getting-started)
  - [Understanding IDs](#understanding-ids)
  - [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [General & Fixtures](#general--fixtures)
  - [Player & Gameweek Data](#player--gameweek-data)
  - [Manager Data](#manager-data)
  - [Leagues](#leagues)
  - [Miscellaneous](#miscellaneous)

---

## Getting Started

### Understanding IDs
To use many of these endpoints, you will need specific IDs.
* **`league_id`**: The unique ID for a league (e.g., mini-league, H2H league).
    * *How to find:* Log in to FPL, click the "Leagues & Cups" tab, select a league. The ID is in the URL.
* **`manager_id`** (or `entry_id`): The unique ID for a fantasy manager/team.
    * *How to find:* Log in to FPL, click the "Points" tab. The ID is in the URL (e.g., `.../entry/12345/...`).
* **`element_id`**: The unique ID for a specific football player (found in the `bootstrap-static` endpoint).
* **`event_id`**: The Gameweek number (1-38).

### Authentication
Some endpoints (like `my-team` or `transfers-latest`) require authentication.
1.  Log in to [https://fantasy.premierleague.com/](https://fantasy.premierleague.com/).
2.  Open your browser's Developer Tools (Inspect Element) and navigate to the **Network** tab.
3.  Refresh the page or click a tab (like "Pick Team") and look for a request (e.g., `me/`).
4.  In the request headers, find the **`cookie`** header.
5.  Copy the entire value of the cookie.
6.  When making requests (e.g., via Postman or code), include a header named `cookie` with this value.

---

## Endpoints

### General & Fixtures

#### 1. General Information
Returns a summary of the game, including current season settings, teams, players, phases, and gameweek summaries.
* **Endpoint:** `bootstrap-static/`
* **Full URL:** `https://fantasy.premierleague.com/api/bootstrap-static/`

#### 2. Fixtures (All)
Returns an array of all fixture objects for the season. Future fixtures contain summary data (kick-off, difficulty), while past fixtures include detailed stats.
* **Endpoint:** `fixtures/`
* **Full URL:** `https://fantasy.premierleague.com/api/fixtures/`

#### 3. Fixtures by Gameweek
Returns fixtures for a specific gameweek.
* **Endpoint:** `fixtures/?event={event_id}`
* **Full URL:** `https://fantasy.premierleague.com/api/fixtures/?event={event_id}`

#### 14. Event Status
Returns the status of the current gameweek, including bonus points updates and league table processing status.
* **Endpoint:** `event-status/`
* **Full URL:** `https://fantasy.premierleague.com/api/event-status/`

### Player & Gameweek Data

#### 4. Detailed Player Data
Returns detailed summary data for a specific player, including past season history and fixtures for the current season.
* **Endpoint:** `element-summary/{element_id}/`
* **Full URL:** `https://fantasy.premierleague.com/api/element-summary/{element_id}/`

#### 5. Gameweek Live Data
Returns live statistics for every player in a specific gameweek.
* **Endpoint:** `event/{event_id}/live/`
* **Full URL:** `https://fantasy.premierleague.com/api/event/{event_id}/live/`

#### 15. Dream Team
Returns the "Dream Team" (highest scoring players) for a specific gameweek.
* **Endpoint:** `dream-team/{event_id}/`
* **Full URL:** `https://fantasy.premierleague.com/api/dream-team/{event_id}/`

### Manager Data

#### 6. Manager Summary
Returns basic summary data for a given manager.
* **Endpoint:** `entry/{manager_id}/`
* **Full URL:** `https://fantasy.premierleague.com/api/entry/{manager_id}/`

#### 7. Manager's History
Returns a manager's history, including stats for every gameweek this season, past season summaries, and chip usage.
* **Endpoint:** `entry/{manager_id}/history/`
* **Full URL:** `https://fantasy.premierleague.com/api/entry/{manager_id}/history/`

#### 8. Manager's Transfers
Returns a history of all transfers made by a manager in the current season.
* **Endpoint:** `entry/{manager_id}/transfers/`
* **Full URL:** `https://fantasy.premierleague.com/api/entry/{manager_id}/transfers/`

#### 9. Manager's Latest Transfers
**[Auth Required]** Returns transfers for the most recently *completed* gameweek. Does not show ongoing live transfers.
* **Endpoint:** `entry/{manager_id}/transfers-latest/`
* **Full URL:** `https://fantasy.premierleague.com/api/entry/{manager_id}/transfers-latest/`

#### 12. Manager's Team (My Team)
**[Auth Required]** Returns the current team for the authenticated user, including chips used and latest transfers. The `manager_id` in the URL must match the authenticated user.
* **Endpoint:** `my-team/{manager_id}/`
* **Full URL:** `https://fantasy.premierleague.com/api/my-team/{manager_id}/`

#### 13. Manager's Picks by Gameweek
Returns the players picked by a manager for a specific gameweek.
* **Endpoint:** `entry/{manager_id}/event/{event_id}/picks/`
* **Full URL:** `https://fantasy.premierleague.com/api/entry/{manager_id}/event/{event_id}/picks/`

#### 17. My Manager Data
**[Auth Required]** Returns personal data for the authenticated manager.
* **Endpoint:** `me/`
* **Full URL:** `https://fantasy.premierleague.com/api/me/`

### Leagues

#### 10. Classic League Standings
Returns standings for a classic league.
* **Endpoint:** `leagues-classic/{league_id}/standings/`
* **Full URL:** `https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/`
* **Query Params:** `page_new_entries`, `page_standings`, `phase`

#### 11. Head-to-Head League Standings
Returns standings for a Head-to-Head league.
* **Endpoint:** `leagues-h2h-matches/league/{league_id}/`
* **Full URL:** `https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{league_id}/`
* **Query Params:** `page` (e.g., `?page=1`)

#### 18. League Cup Status
Returns the cup status for a given league.
* **Endpoint:** `league/{league_id}/cup-status/`
* **Full URL:** `https://fantasy.premierleague.com/api/league/{league_id}/cup-status/`

### Miscellaneous

#### 16. Set Piece Takers
Returns notes on set-piece takers for all teams.
* **Endpoint:** `team/set-piece-notes/`
* **Full URL:** `https://fantasy.premierleague.com/api/team/set-piece-notes/`

#### 19. Most Valuable Teams
Returns the top 5 most valuable teams.
* **Endpoint:** `stats/most-valuable-teams/`
* **Full URL:** `https://fantasy.premierleague.com/api/stats/most-valuable-teams/`

#### 20. Best Leagues
Returns the best leagues based on the average score of the top 5 players.
* **Endpoint:** `stats/best-classic-leagues/`
* **Full URL:** `https://fantasy.premierleague.com/api/stats/best-classic-leagues/`