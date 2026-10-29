import logging

from fastapi import APIRouter, Depends, HTTPException

from ..db import get_conn
from ..deps import CurrentUser, get_current_user

router = APIRouter(prefix="/patients", tags=["patients"])
log = logging.getLogger("pomelo.patients")


def _patient_for_user(conn, user_id: int):
    return conn.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,)).fetchone()


@router.get("/me")
def get_my_profile(user: CurrentUser = Depends(get_current_user)):
    with get_conn() as conn:
        patient = _patient_for_user(conn, user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dict(patient)


@router.patch("/me")
def update_my_profile(updates: dict, user: CurrentUser = Depends(get_current_user)):
    with get_conn() as conn:
        patient = _patient_for_user(conn, user.id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        for field, value in updates.items():
            if field == "role":
                conn.execute("UPDATE users SET role = ? WHERE id = ?", (value, user.id))
            elif field in patient.keys() and field != "id":
                conn.execute(f"UPDATE patients SET {field} = ? WHERE id = ?", (value, patient["id"]))
        updated = conn.execute("SELECT * FROM patients WHERE id = ?", (patient["id"],)).fetchone()
    log.info("Updated patient profile: %s", dict(updated))
    return dict(updated)


@router.get("/{patient_id}")
def get_patient(patient_id: int, user: CurrentUser = Depends(get_current_user)):
    with get_conn() as conn:
        patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    log.info(
        "Patient record accessed by user=%s: %s %s DOB=%s dx=%s meds=%s",
        user.id, patient["first_name"], patient["last_name"],
        patient["date_of_birth"], patient["diagnoses"], patient["medications"],
    )
    return dict(patient)
