from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
import secrets

from app.db import devices_collection
from app.models import DeviceRegister, DevicePublic
from app.auth import require_role

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/register", response_model=DevicePublic)
async def register_device(
    data: DeviceRegister, current_user=Depends(require_role("caretaker"))
):
    """Caretaker registers a new wearable device for a patient"""
    token = secrets.token_hex(16)
    doc = {
        "patient_id": ObjectId(data.patient_id),
        "device_name": data.device_name,
        "device_token": token,
        "registered_at": datetime.utcnow(),
    }
    result = await devices_collection.insert_one(doc)

    return DevicePublic(
        id=str(result.inserted_id),
        patient_id=data.patient_id,
        device_name=data.device_name,
        device_token=token,
        registered_at=doc["registered_at"],
    )


@router.get("/{patient_id}", response_model=list[DevicePublic])
async def list_devices(
    patient_id: str, current_user=Depends(require_role("caretaker"))
):
    """List all devices linked to a patient"""
    cursor = devices_collection.find({"patient_id": ObjectId(patient_id)})
    devices = []
    async for dev in cursor:
        devices.append(
            DevicePublic(
                id=str(dev["_id"]),
                patient_id=str(dev["patient_id"]),
                device_name=dev["device_name"],
                device_token=dev["device_token"],
                registered_at=dev["registered_at"],
            )
        )
    return devices
