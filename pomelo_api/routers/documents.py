from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .. import config
from ..db import get_conn
from ..deps import CurrentUser, get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/insurance-card", status_code=201)
async def upload_insurance_card(
    file: UploadFile = File(...),
    side: str = Form("front"),
    user: CurrentUser = Depends(get_current_user),
):
    with get_conn() as conn:
        patient = conn.execute("SELECT id FROM patients WHERE user_id = ?", (user.id,)).fetchone()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        dest_dir = config.UPLOAD_DIR / str(patient["id"])
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / file.filename
        dest.write_bytes(await file.read())
        cur = conn.execute(
            "INSERT INTO documents (patient_id, kind, filename) VALUES (?, ?, ?)",
            (patient["id"], f"insurance_card_{side}", file.filename),
        )
    return {"id": cur.lastrowid, "filename": file.filename}


@router.get("/{patient_id}/{filename:path}")
def download_document(patient_id: int, filename: str, user: CurrentUser = Depends(get_current_user)):
    path = config.UPLOAD_DIR / str(patient_id) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(path)
