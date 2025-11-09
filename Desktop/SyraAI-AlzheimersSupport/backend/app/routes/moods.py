from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from ..db import moods_col, patients_col
from ..auth import get_current_user
from ..models import MoodCreate, MoodPublic

router = APIRouter(prefix="/moods", tags=["moods"])

@router.post("/", response_model=MoodPublic)
async def log_mood(m: MoodCreate, user=Depends(get_current_user)):
    # patient can log themselves, caretaker can also log
    ts = m.timestamp or datetime.now(timezone.utc)
    doc = {"patient_id": ObjectId(m.patient_id), "mood": m.mood, "note": m.note, "timestamp": ts}
    res = await moods_col.insert_one(doc)
    return {"id": str(res.inserted_id), "patient_id": m.patient_id, "mood": m.mood, "note": m.note, "timestamp": ts}

@router.get("/trend/{patient_id}", response_model=list[MoodPublic])
async def mood_trend(patient_id: str, days: int = 7, user=Depends(get_current_user)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    cur = moods_col.find({"patient_id": ObjectId(patient_id), "timestamp": {"$gte": since}}).sort("timestamp", 1)
    items = []
    async for d in cur:
        items.append({
            "id": str(d["_id"]),
            "patient_id": str(d["patient_id"]),
            "mood": d["mood"],
            "note": d.get("note"),
            "timestamp": d["timestamp"],
        })
    return items
