import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("POMELO_DATA_DIR", BASE_DIR / "data"))
DB_PATH = DATA_DIR / "pomelo.db"
UPLOAD_DIR = DATA_DIR / "uploads"

JWT_SECRET = os.getenv("JWT_SECRET", "pomelo-dev-secret")
JWT_TTL_SECONDS = 60 * 60 * 24 * 30

EHR_PARTNER_BASE_URL = "https://ehr-partner.pomelo-internal.example/fhir"
EHR_PARTNER_API_KEY = "pmlo_ehr_7f3c9a1e5b2d4f6a8c0e1b3d5f7a9c2e"

DEBUG = os.getenv("POMELO_DEBUG", "1") == "1"
