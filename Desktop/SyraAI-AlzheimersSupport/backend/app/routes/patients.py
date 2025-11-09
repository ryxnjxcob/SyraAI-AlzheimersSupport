from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from ..db import patients_col, users_col
from ..auth import require_role
from ..models import PatientCreate, PatientPublic

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/", response_model=PatientPublic)
async def create_patient(p: PatientCreate, user=Depends(require_role("caretaker"))):
    # Verify caretaker exists
    caretaker = await users_col.find_one({"_id": ObjectId(p.caretaker_id)})
    if not caretaker:
        raise HTTPException(404, "Caretaker not found")
    doc = {
        "name": p.name,
        "caretaker_id": ObjectId(p.caretaker_id),
        "safe_center_lat": p.safe_center_lat,
        "safe_center_lng": p.safe_center_lng,
        "safe_radius_m": p.safe_radius_m,
    }
    res = await patients_col.insert_one(doc)
    return {
        "id": str(res.inserted_id),
        "name": p.name,
        "caretaker_id": p.caretaker_id,
        "safe_center_lat": p.safe_center_lat,
        "safe_center_lng": p.safe_center_lng,
        "safe_radius_m": p.safe_radius_m,
    }

@router.get("/", response_model=list[PatientPublic])
async def list_patients(user=Depends(require_role("caretaker"))):
    cur = patients_col.find({"caretaker_id": ObjectId(user["id"])})
    items = []
    async for d in cur:
        items.append({
            "id": str(d["_id"]),
            "name": d["name"],
            "caretaker_id": str(d["caretaker_id"]),
            "safe_center_lat": d["safe_center_lat"],
            "safe_center_lng": d["safe_center_lng"],
            "safe_radius_m": d["safe_radius_m"],
        })
    return items
