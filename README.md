<div align="center">

# PerformX

### Enterprise Goal Setting & Performance Tracking Portal

![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black) ![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?style=flat-square&logo=fastapi&logoColor=white) ![Tailwind](https://img.shields.io/badge/Tailwind-CSS-38bdf8?style=flat-square&logo=tailwindcss&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=flat-square&logo=postgresql&logoColor=white) ![Vercel](https://img.shields.io/badge/Deployed-Vercel-000000?style=flat-square&logo=vercel&logoColor=white) ![Cost](https://img.shields.io/badge/Cost-%240%2Fmonth-brightgreen?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

A modern role-based goal management portal built to replace spreadsheets with a structured digital workflow — from goal setting to quarterly performance tracking.

### 🚀 [View Live Demo](https://perform-x-ivory.vercel.app)

| | |
|---|---|
| **Frontend** | https://perform-x-ivory.vercel.app |
| **Backend API** | https://performx-1.onrender.com |
| **API Docs** | https://performx-1.onrender.com/docs |

</div>

---

## 🎭 Demo Credentials

| Role | Email | Password |
|---|---|---|
| Admin / HR | pranul@performx.com | Admin@123 |
| Manager (Sales) | akshay@performx.com | Manager@123 |
| Manager (Engineering) | saandeep@performx.com | Manager@123 |
| Employee (Locked Goals) | prince@performx.com | Employee@123 |
| Employee (Returned Goals) | vinayak@performx.com | Employee@123 |
| Employee (Pending Approval) | anshul@performx.com | Employee@123 |
| Employee (Engineering) | prachi@performx.com | Employee@123 |

> All accounts have pre-seeded realistic data. Run `python seed.py` to reset to clean demo state.
> The login page has **demo buttons** to auto-fill credentials instantly.

---

## 🎬 Quick Demo Guide

**Total time: ~8 minutes**

### Step 1 — Employee Creates Goals (2 min)
```
Login as prince@performx.com / Employee@123
  → Dashboard → shows goal summary + window status banner
  → My Goals → click "Add Goal"
  → Add 3 goals with thrust areas and weightage totalling 100%
  → Click "Submit for Approval" on each goal
  → Status changes to SUBMITTED ✓
```

### Step 2 — Manager Reviews (2 min)
```
Login as akshay@performx.com / Manager@123
  → Dashboard → shows pending approvals count
  → Approvals → see employee's submitted goals
  → Return one goal with a comment (e.g. "Target too low")
  → Approve another goal → it locks immediately ✓
```

### Step 3 — Employee Revises Returned Goal (1 min)
```
Back to prince@performx.com
  → Dashboard shows orange "X goals returned" alert
  → Click "View and revise" → see manager's amber comment
  → Edit the goal → Resubmit for Approval ✓
```

### Step 4 — Admin Journey (2 min)
```
Login as pranul@performx.com / Admin@123
  → Cycles page → open/close check-in windows
  → Goals → unlock a locked goal → enter mandatory reason
  → Audit Logs → see UNLOCK + APPROVE entries with timestamps
  → Reports → Export CSV → file downloads instantly ✓
```

### Step 5 — Log Quarterly Achievement (1 min)
```
Back to employee → Achievements page
  → Check window status banner (green = open)
  → Enter actual values for each locked goal
  → Tracking scores compute automatically ✓
```

---

## ✨ Features

| Feature | Description | Status |
|---|---|:---:|
| Goal Creation | Thrust area, UoM type, target, weightage — full validated form | ✅ |
| Validation Engine | Max 8 goals · min 10% each · total = 100% (frontend + backend) | ✅ |
| Approval Workflow | Approve / Return for Rework with inline comments | ✅ |
| Goal Locking | Auto-lock on approval · Admin-only unlock | ✅ |
| Check-in Windows | DB-controlled quarterly windows — enforced strictly | ✅ |
| Progress Score Engine | All 4 UoM types: MIN, MAX, ZERO, TIMELINE | ✅ |
| Shared Goals | Admin pushes KPIs · primary owner syncs achievement | ✅ |
| Audit Trail | Append-only · APPROVE / RETURN / UNLOCK all logged | ✅ |
| CSV / Excel Export | Filterable achievement reports | ✅ |
| Real-time Dashboard | Completion rates · Red / Amber / Green indicators | ✅ |
| Escalation Engine | Configurable N-day rules · Vercel Cron daily at 9 AM | ✅ Bonus |
| Email Notifications | 10 key events via SMTP | ✅ Bonus |
| Analytics Dashboard | QoQ trends · department heatmaps · manager effectiveness | ✅ Bonus |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL via Supabase |
| ORM | SQLAlchemy 2.0 + Alembic migrations |
| Auth | JWT (email + password) |
| Charts | Recharts |
| Email | SMTP / Resend compatible |
| Frontend Hosting | Vercel (Free) |
| Backend Hosting | Render (Free) |
| Cron Jobs | Vercel Cron — daily escalation engine |
| **Total Cost** | **$0 / month** |

---

## 🏗 Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                        USER'S BROWSER                           ║
║                                                                  ║
║   ┌─────────────┐   ┌──────────────────┐   ┌────────────────┐  ║
║   │  Employee   │   │     Manager      │   │  Admin / HR    │  ║
║   │  Dashboard  │   │  Approvals +     │   │  Cycles,Users  │  ║
║   │  Goals      │   │  Team Analytics  │   │  Reports,Audit │  ║
║   └─────────────┘   └──────────────────┘   └────────────────┘  ║
║                                                                  ║
║         React 18 + TypeScript + Vite + Tailwind CSS             ║
║         Hosted on → Vercel (perform-x-ivory.vercel.app)         ║
╚══════════════════════╦═══════════════════════════════════════════╝
                       ║  HTTPS + JWT Token
                       ║
╔══════════════════════▼═══════════════════════════════════════════╗
║                      BACKEND API                                ║
║                                                                  ║
║   FastAPI (Python 3.11)  ·  Hosted on Render                    ║
║   performx-1.onrender.com                                        ║
║                                                                  ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐ ║
║  │  /goals  │ │/checkins │ │/analytics│ │ /admin  /reports   │ ║
║  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘ ║
║                                                                  ║
║   Middleware: JWT Auth · Role-Based Access Control (RBAC)       ║
║   Services:  Score Engine · Window Guard · Email Notifier       ║
╚══════╦═══════════════════════════════════════╦════════════════════╝
       ║                                       ║
╔══════▼══════════════╗             ╔══════════▼═══════════════════╗
║    DATABASE         ║             ║    BACKGROUND JOBS           ║
║                     ║             ║                              ║
║  PostgreSQL         ║             ║  Vercel Cron                 ║
║  (Supabase Free)    ║             ║  Runs daily at 9 AM UTC      ║
║                     ║             ║  → checks overdue goals      ║
║  12 tables          ║             ║  → sends escalation alerts   ║
║  SQLAlchemy ORM     ║             ║  → notifies managers         ║
║  Alembic migrations ║             ║                              ║
╚═════════════════════╝             ╚══════════════════════════════╝

  Deployment: Vercel (frontend) + Render (backend) + Supabase (DB)
  Infrastructure cost: $0 / month
```

### How a request flows

```
User clicks "Approve Goal"
        │
        ▼
React sends  POST /api/goals/{id}/approve
        │    with Authorization: Bearer <JWT>
        ▼
FastAPI verifies JWT → extracts role → confirms role = manager
        │
        ▼
Route handler updates goal status → LOCKED
        │
        ├── Writes to PostgreSQL (Supabase)
        ├── Appends entry to audit_log table
        └── Sends email notification to employee
        │
        ▼
Returns 200 OK → React updates UI instantly
```

---

## 📊 Scoring Engine

| UoM Type | Formula | Example |
|---|---|---|
| **MIN** — higher is better | `(Actual ÷ Target) × 100` | 450k / 500k = 90% |
| **MAX** — lower is better | `(Target ÷ Actual) × 100` | 30 / 50 = 60% → capped at 100% |
| **ZERO** — zero = success | `Actual = 0 → 100%, else 0%` | 0 incidents = 100% |
| **TIMELINE** — on time | `100%` | Completed before deadline |
| **TIMELINE** — in progress | `Elapsed days ÷ Total days × 100` | Partial completion |
| **TIMELINE** — completed late | `100 − (days late × penalty %)` | 4 days late × 5% = 80% |

> Penalty % is set per cycle by Admin (default 5%/day, configurable 0–20%).
> All scores are labelled **"Tracking Score"** — not performance ratings.

---

## 🔄 Goal Status Flow

```
  Employee              Manager                Admin
     │                     │                     │
  Creates              Reviews               Can unlock
     │                     │                     │
  DRAFT ──► SUBMITTED ──► LOCKED ◄─────────────────┘
                │
                ▼
            RETURNED ──► (employee edits) ──► RESUBMITTED ──► LOCKED
```

| Status | Editable By | Next Action |
|---|---|---|
| `DRAFT` | Employee | Submit for approval |
| `SUBMITTED` | Manager (inline) | Approve or Return |
| `RETURNED` | Employee | Revise and Resubmit |
| `RESUBMITTED` | Manager (inline) | Approve or Return |
| `LOCKED` | Admin only (with reason) | Log quarterly achievements |

---

## 🔒 Validation Rules

Enforced on **both** frontend form and backend API:

- Maximum **8 goals** per employee per cycle
- Minimum **10% weightage** per individual goal
- Total weightage must equal exactly **100%**
- Validation runs on Submit — Drafts save freely without restriction
- Backend returns HTTP 400 with field-level errors if any rule is violated
- Weightage accepts integers only (no decimals)
- Goals cannot be edited once `LOCKED` — Admin unlock required
- Shared goals: only weightage is editable by recipients

---

## 👥 User Roles

### 🧑‍💼 Employee
- Create and manage personal goal sheets with up to 8 goals
- Submit goals for manager approval once total weightage = 100%
- Edit returned goals and resubmit with changes visible to manager
- Log quarterly actuals during open check-in windows
- View locked goals, tracking scores, and progress history

### 👔 Manager
- View all pending approvals from direct reports
- Approve, return for rework with mandatory comments
- Edit target and weightage inline before approving
- Add structured quarterly check-in comments per employee
- View team analytics — QoQ trends, goal status breakdown
- Monitor escalation alerts for their team on the dashboard

### 🛡 Admin / HR
- Configure goal-setting and quarterly check-in cycles with open/close dates
- Set per-cycle late completion penalty for Timeline goals (0–20%/day)
- Push shared departmental KPIs to multiple employees at once
- Unlock locked goals with mandatory reason — fully audit-logged
- Export achievement reports as CSV or Excel with filters
- View full audit trail — every status change, unlock, and resubmission
- Manage org hierarchy — users, departments, thrust areas
- View org-wide analytics — department heatmaps, manager effectiveness

---

## 🔐 Environment Variables

### Backend (Render)

| Variable | Required | Description |
|---|:---:|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string (Supabase) |
| `SECRET_KEY` | ✅ | JWT signing key — min 32 characters |
| `ALGORITHM` | ✅ | JWT algorithm — `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Token TTL — `480` (8 hours) |
| `APP_BASE_URL` | ✅ | Frontend URL for CORS — update if URL changes |
| `CRON_SECRET` | ✅ | Protects the Vercel Cron escalation endpoint |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | ⚡ | Email notifications |

> If you change the frontend URL, update `APP_BASE_URL` in Render → Environment.

### Frontend (Vercel)

| Variable | Required | Description |
|---|:---:|---|
| `VITE_API_URL` | ✅ | Backend URL — `https://performx-1.onrender.com` |

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
python seed.py
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

## 🔒 Security Notes

- All API endpoints require a valid JWT token
- Role-based access enforced at route handler level via dependency injection
- `GET /admin/cycles` is readable by all authenticated roles — employees need cycle window dates for the dashboard banner. All write operations are Admin-only
- Audit log is append-only — no update or delete endpoints exist
- Goal unlock requires a mandatory reason and is always audit-logged
- CRON_SECRET header required on escalation cron endpoint

---

## 📁 Project Structure

```
PerformX/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point + CORS
│   │   ├── core/                ← Config, DB engine, JWT deps
│   │   ├── models/              ← 12 SQLAlchemy ORM models
│   │   ├── schemas/             ← Pydantic request/response schemas
│   │   ├── routers/             ← 10 API route handlers
│   │   └── services/
│   │       ├── score_engine.py  ← 4-UoM tracking score computation
│   │       ├── email_service.py ← SMTP email notifications
│   │       └── window_guard.py  ← Check-in window enforcement
│   ├── seed.py                  ← Demo data (12 users, rich states)
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
│       ├── context/             ← Auth context + JWT storage
│       └── api/client.ts        ← Axios instance + JWT interceptor
│
├── vercel.json                  ← Cron schedule + SPA routing
├── WORKING_FLOW.md              ← Full user journey documentation
├── SUBMISSION.md                ← One-page judge summary
└── README.md
```

---

## ✅ Submission Checklist

- [x] Live hosted demo URL — https://perform-x-ivory.vercel.app
- [x] Public GitHub repository with clean commit history
- [x] Architecture diagram (see above)
- [x] Login credentials for all 3 roles with pre-seeded data
- [x] Seed script — `python seed.py`
- [x] All core BRD features implemented and tested
- [x] Validation enforced on **both** frontend AND backend
- [x] Goal locking on approval + Admin unlock with audit trail
- [x] Append-only audit log — APPROVE / RETURN / UNLOCK all recorded
- [x] CSV / Excel export working
- [x] Check-in windows DB-controlled and strictly enforced
- [x] All 4 UoM scoring types implemented correctly
- [x] Shared goals with primary owner sync
- [x] Bonus: Escalation engine with Vercel Cron (daily 9 AM)
- [x] Bonus: Email notifications for all key events
- [x] Bonus: Analytics dashboard with QoQ trends and heatmaps
- [x] Cost: **$0/month** — Vercel + Render + Supabase free tiers
- [x] Mobile responsive UI
- [x] Role-based access control on every API endpoint

---

<div align="center">

Built with ❤️ for **AtomQuest Hackathon 1.0**

React · FastAPI · SQLAlchemy · Supabase · Vercel · Tailwind CSS

</div>
