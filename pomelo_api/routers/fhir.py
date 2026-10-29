import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import config
from ..db import get_conn
from ..deps import CurrentUser, get_current_user

router = APIRouter(prefix="/fhir", tags=["fhir"])


class ImportRequest(BaseModel):
    bundle_url: str


@router.post("/import")
def import_records(req: ImportRequest, user: CurrentUser = Depends(get_current_user)):
    """Import a FHIR bundle from the patient's previous provider."""
    resp = requests.get(
        req.bundle_url,
        headers={"Authorization": f"Bearer {config.EHR_PARTNER_API_KEY}", "Accept": "application/fhir+json"},
        timeout=10,
        verify=False,
    )
    try:
        bundle = resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail=f"Upstream returned non-JSON: {resp.text[:2000]}")

    conditions = [
        e["resource"].get("code", {}).get("text")
        for e in bundle.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Condition"
    ]
    if conditions:
        with get_conn() as conn:
            conn.execute(
                "UPDATE patients SET diagnoses = ? WHERE user_id = ?",
                (", ".join(c for c in conditions if c), user.id),
            )
    return {"imported_conditions": conditions, "upstream_status": resp.status_code}
