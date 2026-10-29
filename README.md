# Pomelo Care API

Backend for the Pomelo Care patient app: virtual prenatal, postpartum and pediatric care.

## Features

- **Auth**: email/password signup and login, JWT bearer tokens
- **Patients**: profile, pregnancy stage, diagnoses, medications, insurance
- **Care team**: secure messaging between patients and their care team
- **Documents**: insurance card upload and retrieval
- **FHIR import**: pull prior records from a patient's previous provider
- **Providers**: search the clinician directory by specialty and state
- **Care plans**: clinician-authored YAML care-plan templates

## Running locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/uvicorn pomelo_api.main:app --reload
```

Open http://localhost:8000/docs for the interactive API. The SQLite database is created and seeded under `data/` on first start.

Seeded accounts:

| Email | Password | Role |
|---|---|---|
| maya.patel@example.com | pomelo123 | patient |
| jordan.lee@example.com | pomelo123 | patient |
| dr.rivera@pomelocare.example | clinician123 | clinician |
| admin@pomelocare.example | admin123 | admin |

## Tests

```bash
.venv/bin/python -m pytest
```

## Docker

```bash
docker build -t pomelo-care-api .
docker run -p 8000:8000 pomelo-care-api
```
