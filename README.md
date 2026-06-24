# NBA Data Sync Service

Continuously synchronize NBA parquet datasets from GitHub into Storage.

## Source Path Configuration

The sync supports either a single source path or multiple source paths.

- `GITHUB_BASE_PATHS` (preferred): comma-separated list of source roots.
- `GITHUB_BASE_PATH`: single source root (backward-compatible fallback).

If both are set, `GITHUB_BASE_PATHS` is used.

### Examples

Single path:

```bash
GITHUB_BASE_PATH=nba/player_box/parquet python src/sync.py
```

Multiple paths in one run:

```bash
GITHUB_BASE_PATHS=nba/team_box/parquet,nba/player_box/parquet,nba/schedules/parquet python src/sync.py
```

Optional limit for quick tests:

```bash
GITHUB_BASE_PATHS=nba/team_box/parquet,nba/player_box/parquet SYNC_MAX_FILES=5 python src/sync.py
```
