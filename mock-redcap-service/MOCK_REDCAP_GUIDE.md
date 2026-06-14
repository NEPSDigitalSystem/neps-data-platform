# NEPS Digital — Mock REDCap Integration Guide

## Overview

While waiting for real REDCap credentials from KNUST/CAIH, all teams should develop against the **Mock REDCap API**. This provides realistic data for Ghana, Sierra Leone, and Tanzania.

## Quick Start

### 1. Backend Team (Samuel)

In your FastAPI app, use the mock client:

```python
from app.services.redcap_mock import RedCapMockClient

# Initialize client
redcap = RedCapMockClient()

# Get participants
participants = redcap.get_participants(country="Ghana")

# Get survey responses
responses = redcap.get_survey_responses(record_id="NEPS-GHA-0001")

# Get distress screenings
alerts = redcap.get_distress_screenings(status="open")
```

### 2. Frontend Team (Eric, Ama, Ghazi)

The mock API is available at:
- **Participants:** `GET http://localhost:8000/api/redcap/participants`
- **Surveys:** `GET http://localhost:8000/api/redcap/participants/{id}/surveys`
- **Stats:** `GET http://localhost:8000/api/redcap/stats`

Example fetch:
```javascript
const response = await fetch('http://localhost:8000/api/redcap/participants?country=Ghana');
const data = await response.json();
// data.data = array of participants
// data.total = total count
```

### 3. Data Engineering (Frank)

Use the export endpoint for ETL:
```python
import requests

# Export all records
response = requests.get('http://localhost:8000/api/redcap/export/records')
data = response.json()

# Export specific fields
response = requests.get(
    'http://localhost:8000/api/redcap/export/records',
    params={'fields': ['record_id', 'anxiety_score', 'depression_score']}
)
```

### 4. Data Analyst (Isaac)

Access mock data directly:
```python
from app.services.redcap_mock import RedCapMockClient

client = RedCapMockClient()
stats = client.get_stats()
print(f"Total participants: {stats['total_participants']}")
print(f"By country: {stats['by_country']}")
print(f"High risk flags: {stats['high_risk_flags']}")
```

### 5. ML/AI Team (Yasmine)

Training data is available via:
```python
client = RedCapMockClient()
all_responses = client.get_survey_responses()

# Convert to DataFrame for ML
import pandas as pd
df = pd.DataFrame(all_responses)
```

## Switching to Real REDCap

When you get real credentials, update `.env`:

```bash
# From:
REDCAP_API_URL=http://neps-backend:8000/api/redcap
REDCAP_MOCK_ENABLED=true

# To:
REDCAP_API_URL=https://kcird.org/api/
REDCAP_API_TOKEN=your_real_token_here
REDCAP_MOCK_ENABLED=false
```

## Mock Data Structure

### Participants (150 total)
- **Ghana:** ~50 (Kumasi, Accra, Ho, Tamale)
- **Sierra Leone:** ~50 (Freetown, Bo, Makeni)
- **Tanzania:** ~50 (Dar es Salaam, Mwanza, Arusha)

### Survey Data
- **Baseline:** All 150 participants
- **Monthly reports:** 85% completion rate (months 1-24)
- **Comprehensive waves:** 6m, 12m, 18m, 24m
- **Distress screenings:** ~10% flagged as high-risk

### WP6 Interventions
- **Enrolled:** 20 participants
- **Sessions:** 8 sessions per participant
- **Attendance:** 70-90% rate

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/redcap/health` | GET | Check connectivity |
| `/api/redcap/participants` | GET | List participants |
| `/api/redcap/participants/{id}` | GET | Get participant |
| `/api/redcap/participants/{id}/surveys` | GET | Get surveys |
| `/api/redcap/participants/{id}/consent` | GET | Get consent |
| `/api/redcap/screenings/distress` | GET | Get distress alerts |
| `/api/redcap/referrals` | POST | Create referral |
| `/api/redcap/wp6/sessions/{id}` | GET | Get WP6 sessions |
| `/api/redcap/export/records` | GET | Export all records |
| `/api/redcap/export/metadata` | GET | Export metadata |
| `/api/redcap/stats` | GET | Project statistics |
