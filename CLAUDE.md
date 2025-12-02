# CLAUDE.md - Extended Vehicle Energy Dataset (eVED) Builder

## Project Overview
This project builds an SQLite database containing the Extended Vehicle Energy Dataset (eVED). It processes vehicle trajectory data, performs map-matching using Valhalla, and generates a comprehensive database with signal data, trajectories, vehicles, and map nodes with H3 spatial indexing.

## Architecture
- **Language**: Python 3.11+
- **Package Manager**: uv
- **Database**: SQLite
- **Map Matching**: Valhalla (containerized)
- **Spatial Indexing**: H3
- **Data Sources**: eVED dataset, VED static data

## Key Components

### Database Schema (sql/eved/)
- `vehicle`: Vehicle information and characteristics
- `trajectory`: Trip-level data with H3 spatial indexes
- `signal`: GPS points and sensor data with H3 indexing
- `node`: Map-matched route nodes

### Source Code Structure
- `src/db/`: Database API and connection management
  - `EvedDb.py`: Main database class
  - `api.py`: Database operations and queries
- `src/common/`: Shared utilities
  - `geomath.py`: Geospatial calculations
- `build.py`: Main build script for processing data

### Configuration
- `config.toml`: Project configuration
- `pyproject.toml`: Python dependencies and metadata

## Development Workflow

### Initial Setup
```bash
# Install dependencies
uv sync

# Download source data
make download-data

# Build signal database
make build-signals
```

### Map Matching Process
```bash
# Start Valhalla container (requires Docker/Podman)
make docker-run  # or make pod-run

# Build map-matched nodes
make build-nodes
```

### Key Dependencies
- `aiosqlite`: Async SQLite operations
- `h3`: H3 spatial indexing
- `pandas`: Data processing
- `numpy`: Numerical computations
- `nicegui`: Web UI components
- `requests`: HTTP requests
- `tqdm`: Progress bars

### Data Flow
1. Raw eVED data downloaded from BitBucket repository
2. Static VED data from Excel files
3. Signal processing and database insertion
4. Map matching via Valhalla container
5. Node generation and spatial indexing

### Testing
Run tests with:
```bash
uv run test_valhalla.py
```

### Output
- Primary database: `data/eved.db` (~4GB)
- Contains processed vehicle trajectories, signals, and map-matched routes
- H3 spatial indexes for efficient geospatial queries

## Notes
- Map matching requires Michigan OSM data from GeoFabrik
- Container initialization may take time depending on system performance
- Trajectory points and map nodes have different granularities
- Project uses Podman as Docker alternative but supports both