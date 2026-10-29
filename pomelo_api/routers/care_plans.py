import yaml
from fastapi import APIRouter, Body, Depends

from ..db import get_conn
from ..deps import CurrentUser, require_role

router = APIRouter(prefix="/care-plans", tags=["care-plans"])


@router.post("/templates", status_code=201)
def import_template(
    raw_yaml: str = Body(..., media_type="text/plain"),
    user: CurrentUser = Depends(require_role("clinician", "admin")),
):
    """Clinicians upload care-plan templates authored as YAML."""
    template = yaml.load(raw_yaml, Loader=yaml.Loader)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO care_plan_templates (name, body) VALUES (?, ?)",
            (template.get("name", "Untitled"), raw_yaml),
        )
    return {"id": cur.lastrowid, "name": template.get("name"), "steps": len(template.get("steps", []))}


@router.get("/templates")
def list_templates(user: CurrentUser = Depends(require_role("clinician", "admin"))):
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name FROM care_plan_templates").fetchall()
    return [dict(r) for r in rows]
