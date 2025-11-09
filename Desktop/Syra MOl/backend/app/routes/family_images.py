from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
import os, shutil
from app.db import family_images_collection
from app.models import FamilyImagePublic
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/family", tags=["Family Images"])

UPLOAD_DIR = "static/family_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=FamilyImagePublic)
async def upload_family_image(
    patient_id: str = Form(...),
    caption: str = Form(None),
    file: UploadFile = File(...),
    current_user=Depends(require_role("caretaker")),
):
    # Save image locally
    filename = f"{datetime.utcnow().timestamp()}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = {
        "patient_id": ObjectId(patient_id),
        "uploaded_by": ObjectId(current_user["_id"]),
        "image_url": f"/static/family_images/{filename}",
        "caption": caption,
        "created_at": datetime.utcnow(),
    }
    result = await family_images_collection.insert_one(doc)

    return FamilyImagePublic(
        id=str(result.inserted_id),
        patient_id=patient_id,
        uploaded_by=str(current_user["_id"]),
        image_url=doc["image_url"],
        caption=caption,
        created_at=doc["created_at"],
    )


@router.get("/{patient_id}", response_model=list[FamilyImagePublic])
async def list_family_images(patient_id: str, current_user=Depends(get_current_user)):
    cursor = family_images_collection.find({"patient_id": ObjectId(patient_id)}).sort(
        "created_at", -1
    )
    images = []
    async for img in cursor:
        images.append(
            FamilyImagePublic(
                id=str(img["_id"]),
                patient_id=str(img["patient_id"]),
                uploaded_by=str(img["uploaded_by"]),
                image_url=img["image_url"],
                caption=img.get("caption"),
                created_at=img["created_at"],
            )
        )
    return images
