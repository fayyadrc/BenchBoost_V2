# Database Schema Documentation

This document outlines the MongoDB collections used in the FPLChatbot application and their respective fields.

## Collections

### 1. `players`
Stores detailed profiles and statistics for all FPL players.
**Source:** FPL API (`bootstrap-static` -> `elements`) via `backend/data/player_injury_status.py`.

**Key Fields:**
- `id` (int): Unique FPL player ID.
- `web_name` (string): Player's display name (e.g., "Haaland").
- `first_name` (string): First name.
- `second_name` (string): Last name.
- `team` (int): ID of the team the player belongs to.
- `element_type` (int): Position ID (1=GK, 2=DEF, 3=MID, 4=FWD).
- `now_cost` (int): Current price (e.g., 140 = £14.0m).
- `total_points` (int): Total FPL points scored this season.
- `status` (string): Availability status (e.g., "a"=available, "d"=doubtful, "i"=injured, "s"=suspended, "u"=unavailable).
- `news` (string): News regarding injury or availability.
- `minutes` (int): Total minutes played.
- `goals_scored` (int): Total goals scored.
- `assists` (int): Total assists.
- `clean_sheets` (int): Total clean sheets.
- `goals_conceded` (int): Total goals conceded.
- `own_goals` (int): Total own goals.
- `penalties_saved` (int): Total penalties saved.
- `penalties_missed` (int): Total penalties missed.
- `yellow_cards` (int): Total yellow cards.
- `red_cards` (int): Total red cards.
- `saves` (int): Total saves.
- `bonus` (int): Total bonus points.
- `bps` (int): Bonus Points System score.
- `influence` (string/float): Influence score.
- `creativity` (string/float): Creativity score.
- `threat` (string/float): Threat score.
- `ict_index` (string/float): ICT Index score.
- `selected_by_percent` (string): Percentage of teams selected by.
- `form` (string): Form rating.
- `points_per_game` (string): Average points per game.
- `_last_updated` (datetime): Timestamp of when the record was last updated in the DB.

### 2. `teams`
Stores information about Premier League teams.
**Source:** FPL API (`bootstrap-static` -> `teams`).

**Key Fields:**
- `id` (int): Unique FPL team ID.
- `name` (string): Full team name (e.g., "Manchester City").
- `short_name` (string): 3-letter abbreviation (e.g., "MCI").
- `code` (int): Internal system code for the team.
- `strength` (int): Overall team strength rating.
- `strength_overall_home` (int): Home strength rating.
- `strength_overall_away` (int): Away strength rating.
- `strength_attack_home` (int): Home attack strength.
- `strength_attack_away` (int): Away attack strength.
- `strength_defence_home` (int): Home defence strength.
- `strength_defence_away` (int): Away defence strength.
- `pulse_id` (int): ID used for linking to other Premier League data sources.

### 3. `gameweeks`
Stores schedule and status of each Gameweek.
**Source:** FPL API (`bootstrap-static` -> `events`).

**Key Fields:**
- `id` (int): Gameweek number (e.g., 1, 2, ... 38).
- `name` (string): Display name (e.g., "Gameweek 1").
- `deadline_time` (string/datetime): ISO timestamp of the transfer deadline.
- `average_entry_score` (int): Average score for this gameweek.
- `highest_score` (int): Highest score achieved in this gameweek.
- `is_previous` (bool): True if this is the most recently completed gameweek.
- `is_current` (bool): True if this is the active gameweek.
- `is_next` (bool): True if this is the upcoming gameweek.
- `finished` (bool): True if all matches in the gameweek are complete and points finalized.
- `data_checked` (bool): True if data has been verified.

### 4. `fixtures`
Stores match fixtures, results, and difficulty ratings.
**Source:** FPL API (`fixtures`).

**Key Fields:**
- `id` (int): Unique fixture ID.
- `event` (int): Gameweek number (can be null if not yet scheduled).
- `team_h` (int): Home team ID.
- `team_a` (int): Away team ID.
- `team_h_score` (int): Home team score (null if not played).
- `team_a_score` (int): Away team score (null if not played).
- `kickoff_time` (string/datetime): ISO timestamp of kickoff.
- `finished` (bool): True if the match is over.
- `minutes` (int): Minutes played (for live matches).
- `started` (bool): True if the match has started.
- `team_h_difficulty` (int): Difficulty rating for the home team (1-5).
- `team_a_difficulty` (int): Difficulty rating for the away team (1-5).
- `stats` (list): Detailed match stats (goals, assists, cards, etc.) if available.

## Indexes

The following indexes are created in `backend/database/ingestion.py` to optimize query performance:

- **Players**: `id` (unique), `web_name`, `second_name`, `team`, `element_type`, compound(`now_cost`, `total_points`).
- **Teams**: `id` (unique), `name`, `short_name`.
- **Gameweeks**: `id` (unique), `is_current`, `is_next`.
- **Fixtures**: `id` (unique), `event`, `team_h`, `team_a`, `kickoff_time`.
