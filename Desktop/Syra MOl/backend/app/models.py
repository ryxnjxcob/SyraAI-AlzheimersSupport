from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime
from bson import ObjectId


Role = Literal["patient", "caretaker"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Role


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role


class PatientCreate(BaseModel):
    name: str
    caretaker_id: str
    safe_center_lat: float
    safe_center_lng: float
    safe_radius_m: float = 150.0


class PatientPublic(BaseModel):
    id: str
    name: str
    caretaker_id: str
    safe_center_lat: float
    safe_center_lng: float
    safe_radius_m: float


class ReminderCreate(BaseModel):
    patient_id: str
    title: str
    when: datetime
    notes: Optional[str] = None


class ReminderPublic(BaseModel):
    id: str
    patient_id: str
    title: str
    when: datetime
    notes: Optional[str] = None
    acknowledged: bool = False


class MoodCreate(BaseModel):
    patient_id: str
    mood: Literal["good", "okay", "low"]
    note: Optional[str] = None
    timestamp: Optional[datetime] = None


class MoodPublic(BaseModel):
    id: str
    patient_id: str
    mood: str
    note: Optional[str] = None
    timestamp: datetime


class LocationPing(BaseModel):
    patient_id: str
    lat: float
    lng: float
    timestamp: Optional[datetime] = None


class AlertPublic(BaseModel):
    {
        "_id": ObjectId,
        "patient_id": ObjectId,
        "type": Literal["geofence_breach", "vital_spike"],
        "subtype": Literal["heart_rate", "body_temp", "spo2", "location"],  # optional
        "message": "High heart rate detected: 132 bpm",
        "details": {
            "heart_rate": 132,
            "body_temp": 37.8,
            "spo2": 94,
            "distance_exceeded": 150,
        },
        "created_at": datetime,
        "resolved": bool,
    }


# =========================
# Comforting Message Models
# =========================
class ComfortMessageCreate(BaseModel):
    patient_id: str
    message: str


class ComfortMessagePublic(BaseModel):
    id: str
    patient_id: str
    message: str
    created_by: str
    created_at: datetime


# =========================
# Family Images
# =========================
class FamilyImageUpload(BaseModel):
    patient_id: str
    image_url: str
    caption: Optional[str] = None


class FamilyImagePublic(BaseModel):
    id: str
    patient_id: str
    uploaded_by: str
    image_url: str
    caption: Optional[str] = None
    created_at: datetime


# =========================
# Family Messages
# =========================
class FamilyMessageCreate(BaseModel):
    patient_id: str
    from_user: str
    message: str


class FamilyMessagePublic(BaseModel):
    id: str
    patient_id: str
    from_user: str
    message: str
    created_at: datetime


# =========================
# Daily Logs
# =========================
class LogCreate(BaseModel):
    patient_id: str
    entry: str


class LogPublic(BaseModel):
    id: str
    patient_id: str
    caretaker_id: str
    entry: str
    timestamp: datetime


# =============================
#  DEVICE REGISTRATION MODELS
# =============================
class DeviceRegister(BaseModel):
    patient_id: str
    device_name: str


class DevicePublic(BaseModel):
    id: str
    patient_id: str
    device_name: str
    device_token: str
    registered_at: datetime


# =============================
#  VITALS MODELS
# =============================
class VitalReading(BaseModel):
    patient_id: str
    heart_rate: int
    body_temp: float
    spo2: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VitalPublic(BaseModel):
    id: str
    patient_id: str
    heart_rate: int
    body_temp: float
    spo2: int
    timestamp: datetime
