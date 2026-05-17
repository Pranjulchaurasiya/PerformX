# PerformX — Goal Setting & Progress Tracking

A full-stack web portal for employee goal setting, approval workflows, quarterly check-ins, and performance analytics.

---

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Frontend | React 18 + TypeScript + Vite + Tailwind |
| Backend  | FastAPI (Python 3.13)                   |
| Database | SQLite (dev) / PostgreSQL (production)  |
| Auth     | JWT (email + password)                  |

---

## Quick Start

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python seed.py          # create DB + demo data
python -m uvicorn app.main:app --reload --port 8000
```
API → http://localhost:8000  
Docs → http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
App → http://localhost:5173

---

## Demo Credentials

| Role     | Email                     | Password      |
|----------|---------------------------|---------------|
| Admin    | pranul@performx.com       | Admin@123     |
| Manager  | akshay@performx.com       | Manager@123   |
| Manager  | saandeep@performx.com     | Manager@123   |
| Employee | prince@performx.com       | Employee@123  |
| Employee | vinayak@performx.com      | Employee@123  |

See `WORKING_FLOW.md` for all 12 accounts and full user journeys.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in values.

| Variable                   | Required | Description                                      |
|----------------------------|----------|--------------------------------------------------|
| `DATABASE_URL`             | Yes      | PostgreSQL or SQLite connection string           |
| `SECRET_KEY`               | Yes      | JWT signing key (min 32 chars)                   |
| `SMTP_USER` / `SMTP_PASS`  | No       | Email notifications (falls back to console log)  |
| `CRON_SECRET`              | Yes*     | Authenticates Vercel Cron job calls              |
| `AZURE_CLIENT_ID`          | No       | Azure AD SSO (not yet implemented)               |

> *Required in production for the escalation cron job to work.  
> Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Security Notes

> **`/admin/cycles` GET endpoint** is readable by all authenticated roles.  
> This is by design — employees need cycle window dates to show the correct  
> "window closed" banner on their dashboard and to save achievement records  
> against the active cycle ID.  
> All POST/PATCH operations on cycles are Admin-only and enforced at the  
> route handler level via `require_admin` dependency.

---

## Cron Job (Escalation Engine)

The escalation engine runs daily at 9 AM via Vercel Cron (configured in `vercel.json`).

It checks for:
- Goals not submitted N days after the goal-setting window opened
- Approvals pending N days after submission
- Check-ins not logged N days into an open quarter window

The cron endpoint is `POST /api/cron/escalations` and requires the `Authorization: Bearer <CRON_SECRET>` header.

---

## Project Structure

```
PerformX/
├── backend/
│   ├── app/
│   │   ├── main.py          ← FastAPI entry point
│   │   ├── core/            ← Config, DB, auth deps
│   │   ├── models/          ← SQLAlchemy models
│   │   ├── schemas/         ← Pydantic schemas
│   │   ├── routers/         ← API route handlers
│   │   └── services/        ← Score engine, email, window guard
│   ├── seed.py              ← Demo data seeder
│   ├── .env                 ← Local environment (git-ignored)
│   └── .env.example         ← Template for environment variables
├── frontend/
│   └── src/
│       ├── pages/           ← Employee / Manager / Admin pages
│       ├── layouts/         ← Role-specific sidebars
│       ├── components/      ← Shared UI components
│       └── api/client.ts    ← Axios + JWT interceptor
├── vercel.json              ← Cron job schedule
├── WORKING_FLOW.md          ← Full user journey documentation
└── README.md
```
