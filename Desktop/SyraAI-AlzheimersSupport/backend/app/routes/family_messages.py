from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from app.db import family_messages_collection
from app.models import FamilyMessageCreate, FamilyMessagePublic
from app.auth import get_current_user

router = APIRouter(prefix="/family/message", tags=["Family Messages"])


@router.post("/", response_model=FamilyMessagePublic)
async def add_family_message(
    data: FamilyMessageCreate, current_user=Depends(get_current_user)
):
    doc = {
        "patient_id": ObjectId(data.patient_id),
        "from_user": ObjectId(data.from_user),
        "message": data.message,
        "created_at": datetime.utcnow(),
    }
    result = await family_messages_collection.insert_one(doc)
    return FamilyMessagePublic(
        id=str(result.inserted_id),
        patient_id=data.patient_id,
        from_user=data.from_user,
        message=data.message,
        created_at=doc["created_at"],
    )


@router.get("/latest/{patient_id}", response_model=FamilyMessagePublic)
async def get_latest_message(patient_id: str, current_user=Depends(get_current_user)):
    msg = await family_messages_collection.find_one(
        {"patient_id": ObjectId(patient_id)}, sort=[("created_at", -1)]
    )
    if not msg:
        raise HTTPException(status_code=404, detail="No messages found")
    return FamilyMessagePublic(
        id=str(msg["_id"]),
        patient_id=str(msg["patient_id"]),
        from_user=str(msg["from_user"]),
        message=msg["message"],
        created_at=msg["created_at"],
    )
