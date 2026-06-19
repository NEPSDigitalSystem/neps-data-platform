# NEPS Data Platform

The NEPS Data Platform is the core data pipeline and analytics engine for the NEPS Digital youth mental health study. It provides:

- **ETL Pipeline**: Extract, transform, and load data from REDCap (or mock REDCap) into a centralized PostgreSQL data warehouse
- **Data Normalization**: Structured data models and SQL views optimized for downstream analytics
- **Sync State Management**: Track sync history and incremental updates
- **Analytics Toolkit**: Pre-built scripts for data quality checks, trend analysis, and risk modeling

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Environment Configuration](#environment-configuration)
4. [CLI Usage](#cli-usage)
5. [Testing](#testing)
6. [Docker Build](#docker-build)
7. [Contributing](#contributing)

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NEPSDigitalSystem/neps-data-platform.git
   cd neps-data-platform
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and REDCap credentials
   ```

5. **Run database migrations**
   ```bash
   python -m etl.main migrate
   ```

6. **Run initial sync**
   ```bash
   python -m etl.main sync --full
   ```

## Architecture Overview

The NEPS Data Platform follows a modular ETL architecture:

```
┌───────────────┐
│  REDCap API   │
│  (or Mock)    │
└───────┬───────┘
        │ Extract
        ▼
┌──────────────────────┐
│  Extract Layer       │
│  - Client Factory    │
│  - Metadata Parser   │
│  - Record Fetch      │
└───────┬──────────────┘
        │ Transform
        ▼
┌──────────────────────┐
│ Transform Layer      │
│  - Normalizer        │
│  - Schema Mapping    │
│  - Type Coercion     │
└───────┬──────────────┘
        │ Load
        ▼
┌──────────────────────┐
│  Load Layer          │
│  - Upsert Logic      │
│  - Sync State        │
│  - SQL Views         │
└───────┬──────────────┘
        │
        ▼
┌──────────────────────┐
│ PostgreSQL Data      │
│ Warehouse            │
└──────────────────────┘
```

## Environment Configuration

| Variable               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `DATABASE_URL`         | PostgreSQL connection string (e.g., `postgresql://user:pass@host:5432/db`) |
| `DATABASE_URL_FILE`    | Path to file containing database URL (for production secrets)              |
| `REDCAP_API_URL`       | Mock or production REDCap base URL                                         |
| `REDCAP_API_TOKEN`     | API token (required when `REDCAP_MOCK_ENABLED=false`)                       |
| `REDCAP_API_TOKEN_FILE`| Path to file containing REDCap API token (for production secrets)           |
| `REDCAP_MOCK_ENABLED`  | `true` for mock API, `false` for real REDCap                               |
| `REDCAP_PROJECT_ID`    | Project identifier stored in sync state                                    |

## CLI Usage

```bash
python -m etl.main <command> [options]
```

### Available Commands

| Command                                   | Description                                                         |
|-------------------------------------------|---------------------------------------------------------------------|
| `health`                                  | Check database and REDCap connectivity                              |
| `migrate`                                 | Apply database migrations                                           |
| `sync`                                    | Run sync operation (incremental in production, full in mock mode)   |
| `sync --full`                             | Full sync refresh (reloads all records)                            |
| `sync --metadata-only`                    | Sync only metadata (no records)                                    |
| `sync --dry-run`                          | Extract data without writing to the database                       |

### Examples

```bash
# Check system health
python -m etl.main health

# Full refresh from REDCap
python -m etl.main sync --full

# Dry run to preview what would be synced
python -m etl.main sync --dry-run
```

## Testing

Run all unit tests:
```bash
pytest tests/ -v
```

Test coverage:
```bash
pytest tests/ --cov=etl --cov-report=html
```

## Docker Build

Build the Docker image:
```bash
docker build -t neps-data-platform:latest .
```

Verify the image is built correctly (no dev files included):
```bash
docker run --rm neps-data-platform:latest ls /app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests
4. Submit a pull request

## License

This project is licensed under the MIT License.
