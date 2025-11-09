from fastapi import APIRouter, Depends
from bson import ObjectId
from datetime import datetime, timezone
from ..db import alerts_collection
from ..auth import get_current_user

router = APIRouter(prefix="/sos", tags=["sos"])


@router.post("/{patient_id}")
async def sos(patient_id: str, user=Depends(get_current_user)):
    doc = {
        "patient_id": ObjectId(patient_id),
        "type": "sos",
        "message": "Patient pressed SOS",
        "created_at": datetime.now(timezone.utc),
    }
    await alerts_col.insert_one(doc)
    return {"ok": True}
