import sqlite3
from contextlib import contextmanager

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'patient'
);
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    phone TEXT,
    due_date TEXT,
    pregnancy_stage TEXT,
    diagnoses TEXT,
    medications TEXT,
    insurance_member_id TEXT,
    care_team_id INTEGER
);
CREATE TABLE IF NOT EXISTS care_teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS care_team_members (
    care_team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    care_team_id INTEGER NOT NULL,
    sender_user_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    state TEXT NOT NULL,
    accepting_patients INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    filename TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS care_plan_templates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    body TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_conn():
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    from .security import hash_password

    with get_conn() as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            return
        users = [
            (1, "maya.patel@example.com", hash_password("pomelo123"), "patient"),
            (2, "jordan.lee@example.com", hash_password("pomelo123"), "patient"),
            (3, "dr.rivera@pomelocare.example", hash_password("clinician123"), "clinician"),
            (4, "admin@pomelocare.example", hash_password("admin123"), "admin"),
        ]
        conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users)
        conn.executemany(
            "INSERT INTO care_teams VALUES (?, ?)",
            [(1, "Prenatal Team A"), (2, "Postpartum Team B")],
        )
        conn.executemany(
            "INSERT INTO care_team_members VALUES (?, ?)",
            [(1, 1), (1, 3), (2, 2), (2, 3)],
        )
        conn.executemany(
            "INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (1, 1, "Maya", "Patel", "1993-04-12", "+1-512-555-0142", "2027-02-03",
                 "second_trimester", "gestational diabetes", "metformin 500mg", "AET-88213490", 1),
                (2, 2, "Jordan", "Lee", "1990-09-27", "+1-646-555-0198", None,
                 "postpartum", "postpartum depression", "sertraline 50mg", "UHC-55120934", 2),
            ],
        )
        conn.executemany(
            "INSERT INTO messages (care_team_id, sender_user_id, body) VALUES (?, ?, ?)",
            [
                (1, 1, "My glucose reading this morning was 142 fasting, is that ok?"),
                (1, 3, "Thanks Maya, let's adjust your metformin. I'll call you at 3pm."),
                (2, 2, "I've been having a really hard time sleeping and feeling down."),
                (2, 3, "Thank you for telling us, Jordan. Let's schedule a check-in today."),
            ],
        )
        conn.executemany(
            "INSERT INTO providers (name, specialty, state, accepting_patients) VALUES (?, ?, ?, ?)",
            [
                ("Dr. Ana Rivera", "OB-GYN", "TX", 1),
                ("Dr. Sam Okafor", "Maternal-Fetal Medicine", "NY", 1),
                ("Lena Brooks, IBCLC", "Lactation", "TX", 1),
                ("Dr. Priya Shah", "Perinatal Psychiatry", "CA", 0),
                ("Kim Nguyen, RD", "Nutrition", "TX", 1),
            ],
        )
