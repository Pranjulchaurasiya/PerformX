# PerformX — Goal Setting & Progress Tracking

---

## 1. HOW TO START THE APP

### Step 1 — Start Backend
```
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
API runs at → http://localhost:8000
API docs at → http://localhost:8000/docs

### Step 2 — Start Frontend (new terminal)
```
cd frontend
npm run dev
```
App runs at → http://localhost:5173

### Step 3 — Open Browser
Go to → http://localhost:5173

---

## 2. LOGIN CREDENTIALS

| Role     | Name            | Email                       | Password      |
|----------|-----------------|-----------------------------|---------------|
| Admin    | Pranul Sharma   | pranul@performx.com         | Admin@123     |
| Manager  | Akshay Verma    | akshay@performx.com         | Manager@123   |
| Manager  | Saandeep Gupta  | saandeep@performx.com       | Manager@123   |
| Employee | Prince Rajput   | prince@performx.com         | Employee@123  |
| Employee | Anshul Tiwari   | anshul@performx.com         | Employee@123  |
| Employee | Vinayak Mishra  | vinayak@performx.com        | Employee@123  |
| Employee | Abhishek Pandey | abhishek@performx.com       | Employee@123  |
| Employee | Sarthak Joshi   | sarthak@performx.com        | Employee@123  |
| Employee | Prachi Agarwal  | prachi@performx.com         | Employee@123  |
| Employee | Priyanshoo Singh| priyanshoo@performx.com     | Employee@123  |
| Employee | Nidhi Saxena    | nidhi@performx.com          | Employee@123  |
| Employee | Prashant Kumar  | prashant@performx.com       | Employee@123  |

> Tip: Click the demo buttons on the login page to auto-fill credentials.

**Team structure:**
- Pranul (Admin) → Akshay (Manager, Sales) → Prince, Anshul, Vinayak, Abhishek, Sarthak
- Pranul (Admin) → Saandeep (Manager, Engineering) → Prachi, Priyanshoo, Nidhi, Prashant

---

## 3. COMPLETE USER JOURNEYS

---

### JOURNEY A — Employee Creates & Submits Goals

```
Login as Prince (Employee)
        │
        ▼
Dashboard → shows goal summary + window status
        │
        ▼
My Goals → click "Add Goal"
        │
        ▼
Fill Goal Form:
  - Thrust Area    → select from dropdown
  - Title          → e.g. "Achieve Q1 Sales Target"
  - UoM Type       → Numeric MIN / MAX / Timeline / Zero
  - Target Value   → e.g. 500000
  - Weightage      → min 10%, all goals must total 100%
        │
        ▼
Save Goal → status = DRAFT
        │
        ▼
Repeat until total weightage = 100% (max 8 goals)
        │
        ▼
Click "Submit for Approval" on each goal
        │
        ▼
Status changes → SUBMITTED
Manager gets notified by email
```

---

### JOURNEY B — Manager Reviews & Approves Goals

```
Login as Akshay (Manager)
        │
        ▼
Dashboard → shows pending approvals count
        │
        ▼
Approvals → list of submitted goals
        │
        ▼
Click a goal → Approval Detail page
        │
        ├── Can edit Target and Weightage inline
        │
        ├── APPROVE → goal status = LOCKED (no more edits)
        │              Employee gets notified
        │
        └── RETURN  → enter a comment → goal goes back to employee
                       Employee gets email with edit link
```

---

### JOURNEY C — Employee Revises a Returned Goal

```
Employee gets email: "Your goals need revision"
        │
        ▼
Login → Dashboard shows orange alert "X goals returned"
        │
        ▼
Click "View and revise" → Goal View page
        │
        ▼
Amber banner shows manager's comment at top
        │
        ▼
Click "Revise" → Edit Goal page (pre-filled)
        │
        ▼
Make changes → Save
        │
        ▼
Click "Resubmit for Approval"
        │
        ▼
Status = RESUBMITTED
Manager sees "Resubmission" amber badge on approvals list
Manager can view diff of what changed
```

---

### JOURNEY D — Employee Logs Quarterly Achievement

```
Login as Prince (Employee)
        │
        ▼
Achievements page
        │
        ▼
Check window status banner:
  - Green  = window is open, you can log
  - Amber  = window closed, shows next open date
        │
        ▼
For each locked goal:
  - Enter Actual Value (or Completion Date for Timeline)
  - Select Status: Not Started / On Track / Completed
  - Click Save
        │
        ▼
System auto-computes Tracking Score:
  MIN goals    → Actual ÷ Target × 100
  MAX goals    → Target ÷ Actual × 100
  Zero goals   → 0 = 100%, else 0%
  Timeline     → On time = 100%, Late = 100 - (days × penalty%)
```

---

### JOURNEY E — Manager Conducts Check-in

```
Login as Akshay (Manager)
        │
        ▼
My Team → see all direct reports with progress %
        │
        ▼
Click an employee → view their goals + achievements
        │
        ▼
Click "Add Check-in"
        │
        ▼
Select:
  - Cycle (quarter)
  - Comment Type: Positive / Needs Improvement / At Risk / Note
  - Comment Text
        │
        ▼
Save → check-in logged, visible in completion dashboard
```

---

### JOURNEY F — Admin Manages the System

```
Login as Admin
        │
        ├── USERS
        │     Add / edit users, assign roles, set manager hierarchy
        │
        ├── CYCLES
        │     Create goal-setting and quarterly windows
        │     Set "Late Completion Penalty" per cycle (default 5%/day)
        │     Activate / deactivate cycles
        │
        ├── SHARED GOALS
        │     Push a departmental KPI to multiple employees at once
        │     Employees can only change weightage, not title/target
        │
        ├── REPORTS
        │     Export achievement data as CSV or Excel
        │     Filter by cycle
        │
        ├── AUDIT LOGS
        │     See every change made after goal lock
        │     Who changed what and when
        │
        └── ANALYTICS
              Org-wide QoQ trends by department
              Department completion heatmap (green/amber/red)
              Goal distribution charts
              Manager effectiveness table (sortable)
```

---

## 4. GOAL STATUS FLOW

```
DRAFT
  │
  └─► SUBMITTED ──────────────────────────────────► LOCKED (approved)
            │                                              │
            └─► RETURNED ──► (employee edits) ──► RESUBMITTED ──► LOCKED
```

| Status      | Who can edit?        | What happens next?          |
|-------------|----------------------|-----------------------------|
| DRAFT       | Employee             | Employee submits            |
| SUBMITTED   | Manager (inline)     | Manager approves or returns |
| RETURNED    | Employee             | Employee resubmits          |
| RESUBMITTED | Manager (inline)     | Manager approves or returns |
| LOCKED      | Admin only (unlock)  | Achievements can be logged  |

---

## 5. SCORING FORMULAS

| UoM Type        | Formula                                      |
|-----------------|----------------------------------------------|
| MIN (higher=better) | Actual ÷ Target × 100                    |
| MAX (lower=better)  | Target ÷ Actual × 100                    |
| Zero            | Actual = 0 → 100%, else 0%                   |
| Timeline (on time)  | 100%                                     |
| Timeline (in progress) | Elapsed days ÷ Total days × 100       |
| Timeline (completed late) | 100 − (days late × penalty %)      |

> Penalty % is set per cycle by Admin (default 5% per day, max 20%).

---

## 6. VALIDATION RULES

```
✓ Total weightage across all goals MUST equal 100%
✓ Minimum weightage per goal = 10%
✓ Maximum goals per employee = 8
✓ Goals cannot be edited once LOCKED (Admin unlock required)
✓ Shared goals: only weightage is editable by recipients
✓ Check-in window must be open to log achievements
```

---

## 7. CHECK-IN SCHEDULE

| Phase          | When Opens  | Purpose                        |
|----------------|-------------|--------------------------------|
| Goal Setting   | May 1       | Create, submit, approve goals  |
| Q1 Check-in    | July        | Log Q1 actuals                 |
| Q2 Check-in    | October     | Log Q2 actuals                 |
| Q3 Check-in    | January     | Log Q3 actuals                 |
| Q4 / Annual    | March/April | Final achievement capture      |

> The system blocks achievement entry when the window is closed.

---

## 8. ESCALATION ENGINE (Auto)

Runs daily at 9 AM via cron. Triggers alerts when:

```
GOAL_NOT_SUBMITTED  → Employee hasn't submitted goals N days after window opens
APPROVAL_PENDING    → Manager hasn't approved goals N days after submission
CHECKIN_OVERDUE     → Employee hasn't logged achievements N days into window
```

Escalation levels:
```
Level 1 → Notify employee + their manager
Level 2 → Notify skip-level manager
Level 3 → Notify HR / Admin
```

Manager sees open escalations as a red badge on their dashboard.

---

## 9. API QUICK REFERENCE

| Endpoint                          | Who    | What                          |
|-----------------------------------|--------|-------------------------------|
| POST /api/auth/login              | All    | Login, get JWT token          |
| GET  /api/goals                   | All    | List goals (role-filtered)    |
| POST /api/goals                   | Emp    | Create a goal                 |
| POST /api/goals/{id}/submit       | Emp    | Submit for approval           |
| POST /api/goals/{id}/approve      | Mgr    | Approve and lock              |
| POST /api/goals/{id}/return       | Mgr    | Return for rework             |
| POST /api/achievements            | Emp    | Log quarterly achievement     |
| GET  /api/checkins/window-status  | All    | Check if window is open       |
| GET  /api/analytics/overview      | Mgr    | Team summary stats            |
| GET  /api/escalations/my-team     | Mgr    | Open escalations for team     |
| GET  /api/reports/achievement/csv | Admin  | Export CSV report             |
| GET  /api/admin/cycles            | Admin  | List/manage cycles            |
| GET  /api/audit                   | Admin  | Full audit trail              |

Full interactive docs → http://localhost:8000/docs

---

## 10. FILE STRUCTURE

```
PerformX/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py        ← Environment settings
│   │   │   ├── database.py      ← SQLAlchemy engine + session
│   │   │   ├── security.py      ← JWT + password hashing
│   │   │   └── deps.py          ← Auth dependencies
│   │   ├── models/              ← Database table definitions
│   │   ├── schemas/             ← Pydantic request/response models
│   │   ├── routers/             ← API route handlers
│   │   └── services/
│   │       ├── score_engine.py  ← Tracking score computation
│   │       ├── email_service.py ← Email notifications
│   │       └── window_guard.py  ← Check-in window validation
│   ├── seed.py                  ← Demo data seeder
│   ├── .env                     ← Environment variables
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── App.tsx              ← Routes + role guards
        ├── context/
        │   └── AuthContext.tsx  ← Login state
        ├── api/
        │   └── client.ts        ← Axios + JWT interceptor
        ├── layouts/             ← Sidebars per role
        ├── pages/
        │   ├── LoginPage.tsx
        │   ├── employee/        ← Dashboard, Goals, Achievements
        │   ├── manager/         ← Dashboard, Approvals, Team, Analytics
        │   └── admin/           ← Users, Cycles, Reports, Analytics
        └── components/          ← Shared UI (badges, modals, charts)
```
