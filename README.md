<div align="center">

# PerformX

### Enterprise Goal Setting & Progress Tracking Portal

[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Vercel](https://img.shields.io/badge/Deployed-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

A modern, role-based goal management system built for organizations to replace spreadsheets with a structured digital workflow — from goal setting to quarterly progress tracking.

### 🚀 [View Live Demo](https://perform-x-ivory.vercel.app)

| | |
|---|---|
| **Frontend** | https://perform-x-ivory.vercel.app |
| **Backend API** | https://performx-1.onrender.com |
| **API Docs** | https://performx-1.onrender.com/docs |

</div>

---

## 🏗 Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                        USER'S BROWSER                           ║
║                                                                  ║
║   ┌─────────────┐  ┌──────────────────┐  ┌──────────────────┐  ║
║   │  Employee   │  │     Manager      │  │   Admin / HR     │  ║
║   │  Dashboard  │  │  Approvals +     │  │  Cycles, Users,  │  ║
║   │  Goals      │  │  Team Analytics  │  │  Reports, Audit  │  ║
║   └─────────────┘  └──────────────────┘  └──────────────────┘  ║
║                                                                  ║
║         React 18 + TypeScript + Vite + Tailwind CSS             ║
║         Hosted on → Vercel (perform-x-ivory.vercel.app)         ║
╚══════════════════════╦═══════════════════════════════════════════╝
                       ║  HTTPS + JWT Token
                       ║
╔══════════════════════▼═══════════════════════════════════════════╗
║                      BACKEND API                                ║
║                                                                  ║
║   FastAPI (Python)  ·  Hosted on Render                         ║
║   performx-1.onrender.com                                        ║
║                                                                  ║
║   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  ║
║   │  /goals  │ │/checkins │ │/analytics│ │ /admin /reports  │  ║
║   └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  ║
║                                                                  ║
║   Middleware: JWT Auth · Role-Based Access Control (RBAC)       ║
║   Services:  Score Engine · Window Guard · Email Notifier       ║
╚══════╦═══════════════════════════════════════╦════════════════════╝
       ║                                       ║
╔══════▼══════════════╗             ╔══════════▼═══════════════════╗
║    DATABASE         ║             ║    BACKGROUND JOBS           ║
║                     ║             ║                              ║
║  PostgreSQL         ║             ║  Vercel Cron                 ║
║  (Supabase)         ║             ║  Runs daily at 9 AM          ║
║                     ║             ║  → checks overdue goals      ║
║  12 tables          ║             ║  → sends escalation alerts   ║
║  SQLAlchemy ORM     ║             ║  → notifies managers         ║
║  Audit-ready        ║             ║                              ║
╚═════════════════════╝             ╚══════════════════════════════╝
```

### How a request flows

```
User clicks "Approve Goal"
        │
        ▼
React sends  POST /api/goals/{id}/approve
        │    with Authorization: Bearer <JWT>
        ▼
FastAPI checks JWT → extracts role → confirms role = manager
        │
        ▼
Route handler updates goal status → LOCKED
        │
        ├── Writes to PostgreSQL (Supabase)
        ├── Appends to audit_log table
        └── Sends email notification to employee
        │
        ▼
Returns 200 OK → React updates UI instantly
```

---

## ✨ Features

| Feature | Description | Status |
|---|---|:---:|
| Goal Creation | Full form with thrust area, UoM type, target, and weightage | ✅ |
| Validation Engine | Max 8 goals, min 10% each, total must equal 100% | ✅ |
| Approval Workflow | Approve / Return for Rework with inline comments | ✅ |
| Goal Locking | Goals lock on approval — admin-only unlock with audit trail | ✅ |
| Check-in Windows | Enforced quarterly windows — DB-controlled open/close dates | ✅ |
| Progress Score Engine | All 4 UoM types: MIN, MAX, ZERO, TIMELINE | ✅ |
| Shared Goals | Admin pushes KPIs to team — primary owner syncs achievement | ✅ |
| Audit Trail | Append-only log — who changed what and when | ✅ |
| CSV / Excel Export | Filterable achievement reports | ✅ |
| Escalation Engine | Vercel Cron daily checks + multi-level alerts | ✅ |
| Email Notifications | Submit, approve, return, unlock events | ✅ |
| Analytics Dashboard | QoQ trends, department heatmaps, manager effectiveness | ✅ |

---

## 🎭 Demo Accounts

| Role | Email | Password |
|---|---|---|
| Admin / HR | pranul@performx.com | Admin@123 |
| Manager (Sales) | akshay@performx.com | Manager@123 |
| Manager (Engineering) | saandeep@performx.com | Manager@123 |
| Employee | prince@performx.com | Employee@123 |
| Employee | prachi@performx.com | Employee@123 |

> Tip: The login page has demo buttons to auto-fill credentials.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL via Supabase |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (email + password) |
| Charts | Recharts |
| Email | SMTP / Resend compatible |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |
| Cron Jobs | Vercel Cron — daily escalation engine |
| Cost | **$0 / month** |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone
```bash
git clone https://github.com/Pranjulchaurasiya/PerformX.git
cd PerformX
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY
python seed.py          # populate demo data
uvicorn app.main:app --reload --port 8000
# API  → http://localhost:8000
# Docs → http://localhost:8000/docs
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# App → http://localhost:5173
```

---

## 🔐 Environment Variables

### Backend (Render)

| Variable | Required | Description |
|---|:---:|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing key (min 32 chars) |
| `ALGORITHM` | ✅ | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | `480` (8 hours) |
| `APP_BASE_URL` | ✅ | Frontend URL for CORS — update if URL changes |
| `CRON_SECRET` | ✅ | Protects the escalation cron endpoint |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | ⚡ | Email notifications |

> If you change the frontend URL, update `APP_BASE_URL` in Render → Environment.

### Frontend (Vercel)

| Variable | Required | Description |
|---|:---:|---|
| `VITE_API_URL` | ✅ | Backend URL e.g. `https://performx-1.onrender.com` |

---

## 👥 User Roles

### 🧑‍💼 Employee
- Create up to 8 goals (total weightage must = 100%)
- Submit goals for manager approval
- Edit returned goals and resubmit
- Log quarterly actuals during open check-in windows
- View tracking scores and progress history

### 👔 Manager
- Review and approve / return goal sheets with comments
- Edit target and weightage inline before approving
- Add quarterly check-in comments per employee
- View team analytics and escalation alerts

### 🛡 Admin / HR
- Configure goal-setting and check-in cycles
- Push shared KPIs to multiple employees
- Unlock locked goals (audit-logged)
- Export achievement reports (CSV / Excel)
- View full audit trail and org-wide analytics

---

## 📊 Scoring Engine

| UoM Type | Formula | Use Case |
|---|---|---|
| **MIN** — higher is better | `Actual ÷ Target × 100` | Sales revenue |
| **MAX** — lower is better | `Target ÷ Actual × 100` | Response time, cost |
| **ZERO** — zero = success | `0 → 100%, else 0%` | Safety incidents |
| **TIMELINE** — on time | `100%` | Completed before deadline |
| **TIMELINE** — in progress | `Elapsed ÷ Total days × 100` | Partial completion |
| **TIMELINE** — completed late | `100 − (days late × penalty%)` | Configurable per cycle |

---

## 🔄 Goal Status Flow

```
  Employee          Manager            Admin
     │                 │                 │
  Creates           Reviews           Can unlock
  DRAFT ──► SUBMITTED ──► LOCKED ◄────────┘
               │
               ▼
           RETURNED ──► (employee edits) ──► RESUBMITTED ──► LOCKED
```

---

## 📁 Project Structure

```
PerformX/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point + CORS
│   │   ├── core/                ← Config, DB engine, JWT
│   │   ├── models/              ← 12 SQLAlchemy ORM models
│   │   ├── schemas/             ← Pydantic request/response
│   │   ├── routers/             ← 10 API route handlers
│   │   └── services/
│   │       ├── score_engine.py  ← Tracking score computation
│   │       ├── email_service.py ← Email notifications
│   │       └── window_guard.py  ← Check-in window enforcement
│   ├── seed.py                  ← Demo data seeder
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── employee/        ← Dashboard, Goals, Achievements
│       │   ├── manager/         ← Dashboard, Approvals, Team
│       │   └── admin/           ← Users, Cycles, Reports, Audit
│       ├── layouts/             ← Role-specific sidebars
│       ├── components/          ← Shared UI components
│       ├── context/             ← Auth context + JWT
│       └── api/client.ts        ← Axios + JWT interceptor
│
├── vercel.json                  ← Cron schedule + SPA routing
└── WORKING_FLOW.md              ← Full user journey docs
```

---

## 📄 License

MIT © 2025 PerformX Team
