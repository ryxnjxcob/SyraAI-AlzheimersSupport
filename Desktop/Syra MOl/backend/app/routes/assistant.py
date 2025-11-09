from fastapi import APIRouter, UploadFile, File
import random

router = APIRouter(prefix="/assistant", tags=["Voice Assistant"])

RESPONSES = [
    "You’re safe. Your family loves you very much.",
    "It’s a beautiful day today. Take a deep breath.",
    "Don’t worry. You’re at home and everything is fine.",
    "You can press the SOS button if you need help.",
]


@router.post("/voice")
async def process_voice(file: UploadFile = File(...)):
    # Placeholder: no real STT or TTS yet.
    # You could integrate OpenAI Whisper here.
    text_response = random.choice(RESPONSES)
    return {"reply": text_response}
