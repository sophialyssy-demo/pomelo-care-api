from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..db import get_conn
from ..deps import CurrentUser, get_current_user

router = APIRouter(prefix="/care-teams", tags=["care-team"])


class NewMessage(BaseModel):
    body: str


@router.get("/{team_id}/messages")
def list_messages(team_id: int, user: CurrentUser = Depends(get_current_user)):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE care_team_id = ? ORDER BY id", (team_id,)
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/{team_id}/messages", status_code=201)
def send_message(team_id: int, msg: NewMessage, user: CurrentUser = Depends(get_current_user)):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO messages (care_team_id, sender_user_id, body) VALUES (?, ?, ?)",
            (team_id, user.id, msg.body),
        )
        row = conn.execute("SELECT * FROM messages WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)
