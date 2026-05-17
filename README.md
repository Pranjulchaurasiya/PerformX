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

<br/>

### [🚀 View Live Demo](https://performx.vercel.app)

</div>

---

## 📸 Screenshots

> **Replace with actual screenshots before submission**

| Login Page | Employee Dashboard | Manager Approvals | Admin Analytics |
|:---:|:---:|:---:|:---:|
| *(screenshot)* | *(screenshot)* | *(screenshot)* | *(screenshot)* |

---

## ✨ Features

| Feature | Description | Status |
|---|---|:---:|
| Goal Creation | Full form with thrust area, UoM type, target, and weightage | ✅ Complete |
| Validation Engine | Max 8 goals, min 10% each, total must equal 100% | ✅ Complete |
| Approval Workflow | Approve / Return for Rework / Reject with inline comments | ✅ Complete |
| Goal Locking | Goals lock on approval — admin-only unlock with audit trail | ✅ Complete |
| Check-in Windows | Enforced quarterly windows — DB-controlled open/close dates | ✅ Complete |
| Progress Score Engine | All 4 UoM types: MIN, MAX, ZERO, TIMELINE (3-case) | ✅ Complete |
| Shared Goals | Admin pushes KPIs to team — primary owner syncs achievement | ✅ Complete |
| Audit Trail | Append-only log — who changed what and when | ✅ Complete |
| CSV / Excel Export | Filterable achievement reports with all required columns | ✅ Complete |
| Escalation Engine | Configurable rules + Vercel Cron daily checks | ✅ Bonus |
| Email Notifications | All key events: submit, approve, return, unlock | ✅ Bonus |
| Analytics Dashboard | QoQ trends, department heatmaps, manager effectiveness | ✅ Bonus |
| Azure AD SSO | Microsoft Entra ID login + org hierarchy sync | ⚡ Bonus |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS + custom component library |
| Backend | FastAPI (Python 3.13) |
| Database | PostgreSQL via Supabase |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (email + password) · Azure AD SSO ready |
| Charts | Recharts |
| Email | SMTP / Resend compatible |
| Hosting | Vercel (frontend) + Render (backend) |
| Cron Jobs | Vercel Cron — daily escalation engine |
| Cost | **$0 / month** |

---

## 🎭 Demo Accounts

> All accounts have pre-seeded data for immediate demo.
> Run `python seed.py` to reset to clean demo state.

| Role | Name | Email | Password |
|---|---|---|---|
| Admin / HR | Pranul Sharma | pranul@performx.com | Admin@123 |
| Manager (Sales) | Akshay Verma | akshay@performx.com | Manager@123 |
| Manager (Engineering) | Saandeep Gupta | saandeep@performx.com | Manager@123 |
| Employee — Locked Goals | Prince Rajput | prince@performx.com | Employee@123 |
| Employee — Returned Goals | Vinayak Mishra | vinayak@performx.com | Employee@123 |
| Employee — Pending Approval | Anshul Tiwari | anshul@performx.com | Employee@123 |
| Employee — Draft Goals | Sarthak Joshi | sarthak@performx.com | Employee@123 |
| Employee — Engineering | Prachi Agarwal | prachi@performx.com | Employee@123 |

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/[username]/performx.git
cd performx
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Fill in: DATABASE_URL, SECRET_KEY, CRON_SECRET
```

### 4. Seed the database
```bash
python seed.py
```

### 5. Start the backend
```bash
uvicorn app.main:app --reload --port 8000
# API → http://localhost:8000
# Docs → http://localhost:8000/docs
```

### 6. Frontend setup (new terminal)
```bash
cd frontend
npm install
npm run dev
# App → http://localhost:5173
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|:---:|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string (Supabase or local) |
| `SECRET_KEY` | ✅ | JWT signing key — min 32 characters |
| `ALGORITHM` | ✅ | JWT algorithm — use `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Token TTL — recommended `480` |
| `APP_BASE_URL` | ✅ | Frontend URL for CORS and email deep-links |
| `CRON_SECRET` | ✅ | Protects the Vercel Cron escalation endpoint |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | ⚡ | Email notifications (falls back to console log) |
| `AZURE_CLIENT_ID` | ⚡ | Azure AD SSO — bonus feature |
| `AZURE_CLIENT_SECRET` | ⚡ | Azure AD SSO — bonus feature |
| `AZURE_TENANT_ID` | ⚡ | Azure AD SSO — bonus feature |
| `TEAMS_WEBHOOK_URL` | ⚡ | Microsoft Teams notifications — bonus feature |

> Generate `SECRET_KEY` and `CRON_SECRET` with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CLIENT LAYER                      │
│   Employee Dashboard | Manager View | Admin / HR    │
│          React 18 + TypeScript + Vite               │
│             Tailwind CSS + Recharts                 │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────┐
│                    API LAYER                        │
│              FastAPI (Python 3.13)                  │
│   /goals  /achievements  /checkins  /analytics      │
│   /reports  /audit  /admin  /escalations            │
│         Middleware: JWT Auth + RBAC                 │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
┌──────────▼──────────┐  ┌────────▼────────────────────┐
│    AUTH SERVICE     │  │        DATA LAYER            │
│  JWT (email/pass)   │  │  SQLAlchemy ORM              │
│  Azure AD SSO ready │  │  PostgreSQL (Supabase)       │
│                     │  │  12 tables · audit-ready     │
└─────────────────────┘  └─────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────┐
│              BACKGROUND SERVICES                    │
│  Vercel Cron (0 9 * * *) → /api/cron/escalations   │
│  SMTP / Resend → Email notifications                │
└─────────────────────────────────────────────────────┘

  Deployment: Vercel (frontend) + Render (backend) + Supabase (DB)
  Infrastructure cost: $0 / month
```

---

## 👥 User Roles

### 🧑‍💼 Employee
- Create and manage personal goal sheets with up to 8 goals
- Submit goals for manager approval once total weightage = 100%
- Edit returned goals and resubmit with changes highlighted
- Log quarterly actuals during open check-in windows
- View locked goals, tracking scores, and progress history

### 👔 Manager (L1)
- View all pending approvals from direct reports
- Approve, return for rework, or reject goal sheets with comments
- Edit target and weightage inline before approving
- Add structured quarterly check-in comments per employee
- View team analytics — QoQ trends, goal status breakdown, completion rates
- Monitor escalation alerts for their team on the dashboard

### 🛡 Admin / HR
- Configure goal-setting and quarterly check-in cycles with open/close dates
- Set per-cycle late completion penalty for Timeline goals (0–20% per day)
- Push shared departmental KPIs to multiple employees at once
- Unlock locked goals with mandatory reason — fully audit-logged
- Export achievement reports as CSV or Excel with filters
- View full audit trail — every status change, unlock, and resubmission
- Manage org hierarchy — users, departments, thrust areas
- View org-wide analytics — department heatmaps, manager effectiveness table

---

## 📊 Scoring Engine

The system computes a **Tracking Score** (not a rating) for each goal based on its Unit of Measurement:

| UoM Type | Formula | Example |
|---|---|---|
| **MIN** — higher is better | `Actual ÷ Target × 100` | Sales revenue |
| **MAX** — lower is better | `Target ÷ Actual × 100` | Response time, cost |
| **ZERO** — zero = success | `0 → 100%, else 0%` | Safety incidents |
| **TIMELINE** — on time | `100%` | Completed before deadline |
| **TIMELINE** — in progress | `Elapsed days ÷ Total days × 100` | Partial completion |
| **TIMELINE** — completed late | `100 − (days late × penalty %)` | Configurable per cycle |

---

## 🔄 Goal Status Flow

```
DRAFT ──► SUBMITTED ──────────────────────────────► LOCKED
               │                                       │
               └──► RETURNED ──► RESUBMITTED ──► LOCKED
                        ▲
               Employee edits and resubmits
```

| Status | Editable By | Next Action |
|---|---|---|
| `DRAFT` | Employee | Submit for approval |
| `SUBMITTED` | Manager (inline) | Approve or Return |
| `RETURNED` | Employee | Revise and Resubmit |
| `RESUBMITTED` | Manager (inline) | Approve or Return |
| `LOCKED` | Admin only (unlock) | Log quarterly achievements |

---

## 🔒 Security Notes

- All API endpoints require a valid JWT token
- Role-based access enforced at the route handler level via dependency injection
- `GET /admin/cycles` is intentionally readable by all authenticated roles — employees need cycle window dates for the dashboard banner. All write operations are Admin-only.
- Audit log is append-only — no update or delete endpoints exist
- Goal unlock requires a mandatory reason and is always audit-logged

---

## 📁 Project Structure

```
PerformX/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point + CORS
│   │   ├── core/                ← Config, DB engine, JWT deps
│   │   ├── models/              ← SQLAlchemy ORM models (12 tables)
│   │   ├── schemas/             ← Pydantic request/response schemas
│   │   ├── routers/             ← API route handlers (10 routers)
│   │   └── services/
│   │       ├── score_engine.py  ← 4-UoM tracking score computation
│   │       ├── email_service.py ← SMTP email notifications
│   │       └── window_guard.py  ← Check-in window enforcement
│   ├── seed.py                  ← Demo data (12 users, rich states)
│   ├── .env.example             ← Environment variable template
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── employee/        ← Dashboard, Goals, Achievements
│       │   ├── manager/         ← Dashboard, Approvals, Team, Analytics
│       │   └── admin/           ← Users, Cycles, Reports, Audit, Analytics
│       ├── layouts/             ← Role-specific sidebars with nav
│       ├── components/          ← Shared UI (badges, modals, charts)
│       ├── context/             ← Auth context + JWT storage
│       └── api/client.ts        ← Axios instance + JWT interceptor
│
├── vercel.json                  ← Cron job schedule (daily 9 AM)
├── WORKING_FLOW.md              ← Full user journey documentation
└── README.md
```

---

## 🏆 Hackathon Submission

**Event:** AtomQuest Hackathon 1.0
**Problem Statement:** In-House Goal Setting & Tracking Portal
**Team:** PerformX

### Evaluation Criteria Coverage

| Criteria | Implementation |
|---|---|
| ✅ Functionality | End-to-end flow: create → approve → check-in → report |
| ✅ BRD Adherence | All Phase 1 & Phase 2 requirements implemented |
| ✅ User Friendliness | Role-based UI, inline validation, helpful error messages |
| ✅ Bug-Free | Validation at both frontend and backend layers |
| ✅ Bonus Features | Escalation engine, analytics, email notifications |
| ✅ Cost Optimisation | $0/month — Vercel + Render + Supabase free tiers |

---

## 📄 License

MIT © 2025 PerformX Team
