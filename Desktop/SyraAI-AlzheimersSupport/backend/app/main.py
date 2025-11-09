from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# ✅ Import all route files from app.routes
from app.routes import (
    auth,
    patients,
    reminders,
    moods,
    locations,
    sos,
    comfort,
    family_images,
    family_messages,
    logs,
    assistant,
    devices,
    vitals,
)

# ✅ Initialize FastAPI app
app = FastAPI(title="SARA Backend")

# ✅ Allow frontend requests (CORS)
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "*"  # temporary during dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Static directories (optional)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ✅ Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ Prefix all API routes with /api
API_PREFIX = "/api"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(patients.router, prefix=API_PREFIX)
app.include_router(reminders.router, prefix=API_PREFIX)
app.include_router(moods.router, prefix=API_PREFIX)
app.include_router(locations.router, prefix=API_PREFIX)
app.include_router(sos.router, prefix=API_PREFIX)
app.include_router(comfort.router, prefix=API_PREFIX)
app.include_router(family_images.router, prefix=API_PREFIX)
app.include_router(family_messages.router, prefix=API_PREFIX)
app.include_router(logs.router, prefix=API_PREFIX)
app.include_router(assistant.router, prefix=API_PREFIX)
app.include_router(devices.router, prefix=API_PREFIX)
app.include_router(vitals.router, prefix=API_PREFIX)
