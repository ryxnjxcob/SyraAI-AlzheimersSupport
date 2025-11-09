from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from bson import ObjectId
from app.db import comfort_collection
from app.models import ComfortMessageCreate, ComfortMessagePublic
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/comfort", tags=["Comforting Messages"])


@router.post("/", response_model=ComfortMessagePublic)
async def add_message(
    data: ComfortMessageCreate, current_user=Depends(require_role("caretaker"))
):
    doc = {
        "patient_id": ObjectId(data.patient_id),
        "message": data.message,
        "created_by": ObjectId(current_user["_id"]),
        "created_at": datetime.utcnow(),
    }
    result = await comfort_collection.insert_one(doc)
    return ComfortMessagePublic(
        id=str(result.inserted_id),
        patient_id=data.patient_id,
        message=data.message,
        created_by=str(current_user["_id"]),
        created_at=doc["created_at"],
    )


@router.get("/{patient_id}", response_model=ComfortMessagePublic)
async def get_latest_message(patient_id: str, current_user=Depends(get_current_user)):
    msg = await comfort_collection.find_one(
        {"patient_id": ObjectId(patient_id)}, sort=[("created_at", -1)]
    )
    if not msg:
        raise HTTPException(status_code=404, detail="No comforting message found")
    return ComfortMessagePublic(
        id=str(msg["_id"]),
        patient_id=str(msg["patient_id"]),
        message=msg["message"],
        created_by=str(msg["created_by"]),
        created_at=msg["created_at"],
    )
