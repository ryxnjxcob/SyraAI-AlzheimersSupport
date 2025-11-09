from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timedelta
from bson import ObjectId

from app.db import vitals_collection, alerts_collection, devices_collection
from app.models import VitalReading, VitalPublic

router = APIRouter(prefix="/vitals", tags=["Vitals"])

# Safety thresholds
MAX_HEART_RATE = 120
MIN_HEART_RATE = 40
MAX_TEMP = 38.0
MIN_SPO2 = 90


async def verify_device_token(device_token: str = Header(...)):
    """Authenticate the wearable device using its unique token."""
    device = await devices_collection.find_one({"device_token": device_token})
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device token")
    return device


@router.post("/", response_model=VitalPublic)
async def record_vitals(data: VitalReading, device=Depends(verify_device_token)):
    """Record vital signs sent from the wearable pendant"""
    doc = {
        "patient_id": ObjectId(data.patient_id),
        "heart_rate": data.heart_rate,
        "body_temp": data.body_temp,
        "spo2": data.spo2,
        "timestamp": datetime.utcnow(),
    }

    result = await vitals_collection.insert_one(doc)

    # Check thresholds and trigger alert if abnormal
    alert_type = None
    message = None
    if data.heart_rate > MAX_HEART_RATE:
        alert_type = "vital_spike"
        message = f"High heart rate detected: {data.heart_rate} bpm"
    elif data.heart_rate < MIN_HEART_RATE:
        alert_type = "vital_drop"
        message = f"Low heart rate detected: {data.heart_rate} bpm"
    elif data.body_temp > MAX_TEMP:
        alert_type = "vital_spike"
        message = f"High temperature detected: {data.body_temp}°C"
    elif data.spo2 < MIN_SPO2:
        alert_type = "vital_spike"
        message = f"Low SpO₂ detected: {data.spo2}%"

    if alert_type:
        await alerts_collection.insert_one(
            {
                "patient_id": ObjectId(data.patient_id),
                "type": alert_type,
                "message": message,
                "created_at": datetime.utcnow(),
                "resolved": False,
            }
        )

    return VitalPublic(
        id=str(result.inserted_id),
        patient_id=data.patient_id,
        heart_rate=data.heart_rate,
        body_temp=data.body_temp,
        spo2=data.spo2,
        timestamp=doc["timestamp"],
    )


@router.get("/latest/{patient_id}", response_model=VitalPublic)
async def get_latest_vitals(patient_id: str):
    """Get latest vitals for a patient"""
    reading = await vitals_collection.find_one(
        {"patient_id": ObjectId(patient_id)}, sort=[("timestamp", -1)]
    )
    if not reading:
        raise HTTPException(status_code=404, detail="No vitals found")
    return VitalPublic(
        id=str(reading["_id"]),
        patient_id=str(reading["patient_id"]),
        heart_rate=reading["heart_rate"],
        body_temp=reading["body_temp"],
        spo2=reading["spo2"],
        timestamp=reading["timestamp"],
    )


@router.get("/history/{patient_id}", response_model=list[VitalPublic])
async def get_vitals_history(patient_id: str, hours: int = 24):
    """Get vitals history for the last X hours"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    cursor = vitals_collection.find(
        {"patient_id": ObjectId(patient_id), "timestamp": {"$gte": cutoff}}
    ).sort("timestamp", -1)

    results = []
    async for doc in cursor:
        results.append(
            VitalPublic(
                id=str(doc["_id"]),
                patient_id=str(doc["patient_id"]),
                heart_rate=doc["heart_rate"],
                body_temp=doc["body_temp"],
                spo2=doc["spo2"],
                timestamp=doc["timestamp"],
            )
        )
    return results
