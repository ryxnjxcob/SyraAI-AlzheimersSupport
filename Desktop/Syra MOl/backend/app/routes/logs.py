from fastapi import APIRouter, Depends
from datetime import datetime
from bson import ObjectId
from app.db import logs_collection
from app.models import LogCreate, LogPublic
from app.auth import require_role

# ✅ This is what FastAPI looks for
router = APIRouter(prefix="/logs", tags=["Daily Logs"])


@router.post("/", response_model=LogPublic)
async def create_log(data: LogCreate, current_user=Depends(require_role("caretaker"))):
    """Caretaker adds a daily log/observation for a patient"""
    doc = {
        "patient_id": ObjectId(data.patient_id),
        "caretaker_id": ObjectId(current_user["_id"]),
        "entry": data.entry,
        "timestamp": datetime.utcnow(),
    }
    result = await logs_collection.insert_one(doc)

    return LogPublic(
        id=str(result.inserted_id),
        patient_id=data.patient_id,
        caretaker_id=str(current_user["_id"]),
        entry=data.entry,
        timestamp=doc["timestamp"],
    )


@router.get("/{patient_id}", response_model=list[LogPublic])
async def list_logs(patient_id: str, current_user=Depends(require_role("caretaker"))):
    """Fetch all logs for a specific patient"""
    cursor = logs_collection.find({"patient_id": ObjectId(patient_id)}).sort(
        "timestamp", -1
    )
    logs = []
    async for log in cursor:
        logs.append(
            LogPublic(
                id=str(log["_id"]),
                patient_id=str(log["patient_id"]),
                caretaker_id=str(log["caretaker_id"]),
                entry=log["entry"],
                timestamp=log["timestamp"],
            )
        )
    return logs
