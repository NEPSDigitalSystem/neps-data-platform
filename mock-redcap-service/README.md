# NEPS Digital — Mock REDCap Service

Temporary mock REDCap API for development. Provides realistic longitudinal data across Ghana, Sierra Leone, and Tanzania.

## Files

| File | Purpose |
|------|---------|
| `app/services/redcap_mock.py` | Core mock client with 150 participants, 24-month data |
| `app/routers/redcap_mock.py` | FastAPI endpoints |
| `.env.example` | Environment configuration |
| `docker-compose.mock.yml` | Docker Compose with mock enabled |
| `MOCK_REDCAP_GUIDE.md` | Team integration guide |

## Usage

```bash
# Start with mock data
docker-compose -f docker-compose.mock.yml up --build

# Access mock API
curl http://localhost:8000/api/redcap/stats
curl http://localhost:8000/api/redcap/participants?country=Ghana
```

## Data Generated

- **150 participants** across 3 countries, 10 sites
- **24 months** of longitudinal self-reports
- **Comprehensive waves** at 6, 12, 18, 24 months
- **Distress screenings** with safeguarding flags
- **WP6 intervention** sessions for 20 participants
- **Consent tracking** with re-consent workflows

## When Real REDCap is Available

1. Get API URL + token from KNUST/CAIH coordinator
2. Update `.env` with real credentials
3. Set `REDCAP_MOCK_ENABLED=false`
4. Replace mock client with real REDCap API client
