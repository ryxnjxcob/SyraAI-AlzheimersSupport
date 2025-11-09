from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from ..db import reminders_col, patients_col
from ..auth import require_role, get_current_user
from ..models import ReminderCreate, ReminderPublic

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("/", response_model=ReminderPublic)
async def create_reminder(r: ReminderCreate, user=Depends(require_role("caretaker"))):
    pat = await patients_col.find_one({"_id": ObjectId(r.patient_id), "caretaker_id": ObjectId(user["id"])})
    if not pat:
        raise HTTPException(404, "Patient not found")
    doc = {
        "patient_id": ObjectId(r.patient_id),
        "title": r.title,
        "when": r.when,
        "notes": r.notes,
        "acknowledged": False,
    }
    res = await reminders_col.insert_one(doc)
    return {"id": str(res.inserted_id), **{k: doc[k] for k in ["patient_id","title","when","notes","acknowledged"]}}

@router.get("/due/{patient_id}", response_model=list[ReminderPublic])
async def due_reminders(patient_id: str, user=Depends(get_current_user)):
    # Patient or caretaker can fetch
    cur = reminders_col.find({
        "patient_id": ObjectId(patient_id),
        "when": {"$lte": datetime.now(timezone.utc)},
        "acknowledged": False
    })
    items = []
    async for d in cur:
        items.append({
            "id": str(d["_id"]),
            "patient_id": str(d["patient_id"]),
            "title": d["title"],
            "when": d["when"],
            "notes": d.get("notes"),
            "acknowledged": d["acknowledged"]
        })
    return items

@router.post("/{reminder_id}/ack")
async def ack(reminder_id: str, user=Depends(get_current_user)):
    res = await reminders_col.update_one({"_id": ObjectId(reminder_id)}, {"$set": {"acknowledged": True}})
    if res.matched_count == 0:
        raise HTTPException(404, "Reminder not found")
    return {"ok": True}
