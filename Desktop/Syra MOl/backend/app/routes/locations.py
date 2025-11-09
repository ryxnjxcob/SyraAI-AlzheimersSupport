from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from ..db import locations_col, patients_col, alerts_collection, users_col
from ..auth import get_current_user
from ..models import LocationPing, AlertPublic
from ..utils.geo import haversine_m

router = APIRouter(prefix="/locations", tags=["locations"])


async def maybe_create_alert(patient_id: str, kind: str, message: str):
    doc = {
        "patient_id": ObjectId(patient_id),
        "type": kind,
        "message": message,
        "created_at": datetime.now(timezone.utc),
    }
    res = await alerts_collection.insert_one(doc)
    # Twilio/email hook could be called here (optional no-op if not configured)
    return str(res.inserted_id)


@router.post("/ping", response_model=dict)
async def ping(loc: LocationPing, user=Depends(get_current_user)):
    ts = loc.timestamp or datetime.now(timezone.utc)
    doc = {
        "patient_id": ObjectId(loc.patient_id),
        "lat": loc.lat,
        "lng": loc.lng,
        "timestamp": ts,
    }
    await locations_col.insert_one(doc)

    # Geofence check
    pat = await patients_col.find_one({"_id": ObjectId(loc.patient_id)})
    if pat:
        dist_m = haversine_m(
            pat["safe_center_lat"], pat["safe_center_lng"], loc.lat, loc.lng
        )
        if dist_m > pat["safe_radius_m"]:
            await maybe_create_alert(
                loc.patient_id,
                "geofence_breach",
                f"Patient left safe zone by {int(dist_m - pat['safe_radius_m'])} m",
            )

    return {"ok": True}


@router.get("/latest/{patient_id}")
async def latest(patient_id: str, user=Depends(get_current_user)):
    d = await locations_col.find_one(
        {"patient_id": ObjectId(patient_id)}, sort=[("timestamp", -1)]
    )
    if not d:
        raise HTTPException(404, "No locations yet")
    d["id"] = str(d["_id"])
    d["patient_id"] = str(d["patient_id"])
    d.pop("_id", None)
    return d


@router.get("/alerts/{patient_id}", response_model=list[AlertPublic])
async def alerts(patient_id: str, user=Depends(get_current_user)):
    cur = alerts_collection.find({"patient_id": ObjectId(patient_id)}).sort(
        "created_at", -1
    )
    items = []
    async for d in cur:
        items.append(
            {
                "id": str(d["_id"]),
                "patient_id": str(d["patient_id"]),
                "type": d["type"],
                "message": d["message"],
                "created_at": d["created_at"],
            }
        )
    return items
