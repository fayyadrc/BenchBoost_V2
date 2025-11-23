# BenchBoost MongoDB Schema

This document summarizes MongoDB collections, document fields (conceptual), and recommended refresh cadences.

## Collections Overview

| Collection | Purpose | Key Fields | Refresh Cadence |
|------------|---------|-----------|-----------------|
| `players` | Canonical player metadata & season stats snapshot | `id`, names, team, status, cost, points | Daily (bootstrap-static) |
| `teams` | Team metadata & strength metrics | `id`, name, short_name, strength fields | Rare (bootstrap/static) |
| `gameweeks` | Gameweek deadlines & status | `id`, name, deadline_time, is_current flags | Daily / on deadline flip |
| `fixtures` | Match schedule & results | `id`, event, team_h/team_a, scores, kickoff_time | Daily; higher frequency on match days |
| `player_gameweek_stats` | Per-player GW performance snapshot | `player_id`, `event`, stats & total_points | After each match window / post-GW |
| `managers` | FPL manager identity & season-level summary | `entry_id`, team_name, overall rank/points | Daily |
| `manager_gameweeks` | Per manager GW summary | `entry_id`, `event`, points, rank, transfers | Post-GW or on demand |
| `manager_picks` | Manager squad & captaincy for a GW | `entry_id`, `event`, element, position | At lock / on request |
| `transfers` | Manager transfer history | `entry_id`, element_in/out, time | After each new transfer detected |
| `price_changes` | Player price movement history | `player_id`, direction, new_price, captured_at | Daily (scrape) |
| `status_updates` | Player injury/availability updates | `player_id`, status, news, captured_at | Daily (scrape) |
| `livefpl_snapshots` | LiveFPL overall GW summary | `entry_id`, `event`, rank_direction, safety_score | On-demand / limited retention |
| `differentials_snapshots` | Owned low-EO players snapshot | entry_id, event, player_id, ownership | On-demand |
| `threats_snapshots` | Non-owned high-EO players snapshot | entry_id, event, player_id, ownership | On-demand |
| `captain_performance` | Captain outcome summary | entry_id, event, captain_player_id, result | After captain points finalize |

## Index Strategy

Indexes created in `backend/database/mongo.py`:
- `players`: `id` (unique), `web_name`, `team`, `element_type`
- `teams`: `id` (unique), `short_name`
- `gameweeks`: `id` (unique), `is_current`
- `fixtures`: `id` (unique), `event`, `team_h`, `team_a`
- `player_gameweek_stats`: compound unique (`player_id`, `event`)
- `price_changes`: compound (`player_id`, `captured_at`)
- `status_updates`: compound (`player_id`, `captured_at`)
- `managers`: `entry_id` (unique)
- `manager_gameweeks`: compound unique (`entry_id`, `event`)
- `manager_picks`: compound (`entry_id`, `event`), single (`element`)
- `transfers`: compound (`entry_id`, `time`)

Additional recommended future indexes:
- Live snapshot collections: (`entry_id`, `event`, `captured_at`)

## Document Model Notes

All Pydantic models live in `backend/database/schemas.py` and include an `updated_at` timestamp (except simple snapshot/time-series docs) to support freshness checks.

### Players
Stores current season snapshot of the player (mirrors bootstrap-static element subset). Historical changes (e.g., price or status) tracked separately in `price_changes` and `status_updates`.

### Player Gameweek Stats
Stores finalized performance metrics per gameweek. Do not ingest partial (mid-match) states unless you want live deltas—prefer final snapshots for analytical integrity.

### Manager Data
`managers` holds season-level summary fields; granular GW performance in `manager_gameweeks`; picks in `manager_picks`; transactional history in `transfers`.

### Time-Series Collections
`price_changes` and `status_updates` are append-only. Avoid overwriting previous captures—each represents a point-in-time state.

### LiveFPL Snapshots
Intended for session-level analytics and visualizations. Consider retention policy (e.g., keep last N snapshots per GW) to cap storage.

## Refresh Cadence Summary

- High Frequency (match windows): `player_gameweek_stats` (optional mid-match), `fixtures` (scores), live snapshots.
- Daily: `players`, `gameweeks`, `price_changes`, `status_updates`, `managers`.
- Post-GW: `manager_gameweeks`, `manager_picks` (finalized), captain performance.
- Event-Driven: `transfers` (poll periodically), captain performance when captain’s match ends.

## ETL Functions

Defined in `backend/database/ingest.py`:
- `ingest_bootstrap()` – Upserts players, teams, gameweeks.
- `ingest_fixtures(event=None)` – Upserts fixtures (all or by GW).
- `ingest_event_live(event)` – Upserts per-player GW stats.
- `full_bootstrap_refresh()` – Convenience combined run.

## Future Enhancements
- Add embedding metadata collections for RAG (rules, player bios, fixture context).
- Implement soft-deletion or archival strategy for older seasons (partition by season key).
- Add a `season` field to collections that require multi-season retention (players, stats, gameweeks, fixtures).
- Introduce a `version` field in `gameweeks` for postponed/rescheduled fixture tracking.

## Usage Examples

```python
from backend.database.ingest import ingest_bootstrap, ingest_fixtures
from backend.database.mongo import ensure_indexes

ensure_indexes()
print(ingest_bootstrap())
print(ingest_fixtures())
```

## Operational Notes
- Use environment variables `MONGO_URI` and `MONGO_DB_NAME` for deployment flexibility.
- Wrap ingestion calls in try/except to log HTTP or network errors from upstream API calls.
- Consider idempotent scheduling (e.g., run bootstrap nightly; detect unchanged payloads via hash to skip writes).

## Retention & Cleanup
- Time-series collections can grow quickly; implement TTL indexes (not yet added) for ephemeral data (`livefpl_snapshots`, `differentials_snapshots`, `threats_snapshots`) if storage constraints emerge.
- Avoid TTL on historical analytical datasets (price changes, status updates) unless explicitly purging after a season rollover.

## Monitoring Suggestions
- Track document counts per collection weekly.
- Add a `last_ingested_at` metadata collection recording timestamps of successful ETL runs.
- Alert if `is_current` gameweek flag mismatch persists after expected deadline flip.
