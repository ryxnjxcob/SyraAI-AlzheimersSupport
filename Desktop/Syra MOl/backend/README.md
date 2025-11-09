# Sara (MVP) — FastAPI + MongoDB

This is a **fully working MVP** backend for *Sara*, plus a **minimal caregiver dashboard** served by FastAPI.
It includes:
- JWT auth (patient / caretaker roles)
- Patients, caregivers, reminders, moods
- GPS location pings + geofence alerts
- Alert feed
- Simple anomaly flag (speed/deviation heuristic); IsolationForest stub for later
- Twilio SMS/email hook (safe no-op if not configured)
- Static dashboard (Tailwind) for caretakers

## Quick Start (Replit-friendly)

1) Create a new **Python** Repl.
2) Upload the entire `backend/` folder contents into your Repl root (or clone this repo).
3) Add a **Secrets** (Environment) with keys from `.env.example` (at least `JWT_SECRET`, `MONGODB_URI`).
   - For local MongoDB alternative, use MongoDB Atlas free tier and paste the URI.
4) Open the Replit Shell and run:
```
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
5) Open the Webview at `https://<your-repl>.<your-username>.repl.co`.
   - Caregiver Dashboard: `/` (static HTML calls API)
   - Interactive API docs: `/docs`

## Environment Variables

Copy `.env.example` to `.env`:
- `APP_NAME` (default: Sara)
- `JWT_SECRET` (required)
- `JWT_EXPIRE_MINUTES` (default: 43200 i.e., 30 days)
- `MONGODB_URI` (required) — e.g., mongodb+srv://... (Atlas)
- `DB_NAME` (default: sara)
- `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_FROM` (optional)
- `ALERT_EMAIL_TO` (optional; for demo we just log)

## Roles
- `role`: `"patient"` or `"caretaker"`

## Basic Flow

1) **Register** caretaker → create **patient** profile (with `safe_center` + `safe_radius_m`).
2) Patient logs in on the patient device, **pings location** periodically.
3) Backend checks geofence; if breached, creates an **alert** and calls Twilio hook.
4) Patient logs **mood**; caregiver sees **trend** in dashboard.
5) Caregiver creates **reminders**; patient device can fetch due reminders.

---

This MVP is intentionally compact and readable so you can extend it (Next.js frontend, ML models, wearables, etc.).
