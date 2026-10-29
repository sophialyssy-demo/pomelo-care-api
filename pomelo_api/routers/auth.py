from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import get_conn
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone: str | None = None


@router.post("/login")
def login(body: LoginRequest):
    with get_conn() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (body.email,)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="No account found for that email")
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"access_token": create_access_token(user["id"], user["role"]), "token_type": "bearer"}


@router.post("/signup", status_code=201)
def signup(body: SignupRequest):
    with get_conn() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email = ?", (body.email,)).fetchone():
            raise HTTPException(status_code=409, detail="Email already registered")
        cur = conn.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'patient')",
            (body.email, hash_password(body.password)),
        )
        user_id = cur.lastrowid
        conn.execute(
            "INSERT INTO patients (user_id, first_name, last_name, date_of_birth, phone) VALUES (?, ?, ?, ?, ?)",
            (user_id, body.first_name, body.last_name, body.date_of_birth, body.phone),
        )
    return {"access_token": create_access_token(user_id, "patient"), "token_type": "bearer"}
