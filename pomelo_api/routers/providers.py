from fastapi import APIRouter, Depends

from ..db import get_conn
from ..deps import CurrentUser, get_current_user

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/search")
def search_providers(
    specialty: str = "",
    state: str = "",
    sort: str = "name",
    user: CurrentUser = Depends(get_current_user),
):
    query = "SELECT id, name, specialty, state, accepting_patients FROM providers WHERE 1=1"
    if specialty:
        query += f" AND specialty LIKE '%{specialty}%'"
    if state:
        query += f" AND state = '{state}'"
    query += f" ORDER BY {sort}"
    with get_conn() as conn:
        rows = conn.execute(query).fetchall()
    return [dict(r) for r in rows]
