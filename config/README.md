# Dynamic Configuration

This directory contains configuration files that can be edited directly on GitHub to update the application without code changes.

## Files

### `indicators.json` (Future)
- Will contain indicator definitions
- Currently indicators are defined in `backend/app/country/catalog.py`
- Future migration to JSON for easier GitHub-based updates

### `sources.json` (Future)
- Will contain source ratings and feed URLs
- Currently defined in `backend/app/constants.py` and `backend/app/ingest/feeds.py`
- Future migration to JSON for easier GitHub-based updates

## GitHub-Based Updates

Once migrated to JSON:
1. Edit the JSON file directly on GitHub
2. Commit the change
3. Application reloads configuration on next deployment
4. No code changes required

## Current State

Configuration is currently hardcoded in Python files:
- `backend/app/country/catalog.py` - Indicator catalog
- `backend/app/constants.py` - Source ratings, categories
- `backend/app/ingest/feeds.py` - News feed URLs

This is acceptable for now. Migration to JSON will be done when:
- Non-technical users need to update indicators/sources
- Frequent configuration changes are expected
- Multiple environments (dev/staging/prod) need different configs
