# PerformX — Hackathon Submission Summary

**Team:** Pranjul Chaurasiya
**Event:** AtomQuest Hackathon 1.0
**Category:** Web Application — Goal Setting & Performance Tracking Portal

---

## 🚀 Live Demo

| | |
|---|---|
| **App URL** | https://perform-x-ivory.vercel.app |
| **API Docs** | https://performx-1.onrender.com/docs |
| **Repository** | https://github.com/Pranjulchaurasiya/PerformX |

**Login instantly with:**

| Role | Email | Password |
|---|---|---|
| Admin / HR | pranul@performx.com | Admin@123 |
| Manager | akshay@performx.com | Manager@123 |
| Employee | prince@performx.com | Employee@123 |

> The login page has **demo buttons** — one click to auto-fill any role.

---

## 🏗 What We Built

An enterprise-grade goal setting and performance tracking portal that replaces spreadsheets with a structured, role-based digital workflow. Three distinct user roles, quarterly check-in cycles, strict validation, real-time scoring, and full audit compliance — all running at **$0/month**.

**Stack:** React 18 + TypeScript · FastAPI (Python) · PostgreSQL (Supabase) · Vercel + Render

---

## ✅ Core BRD Requirements Met

| Requirement | Status |
|---|:---:|
| Max 8 goals per employee per cycle | ✅ |
| Min 10% weightage per goal | ✅ |
| Total weightage = 100% (frontend + backend validation) | ✅ |
| Manager approve / return for rework workflow | ✅ |
| Goal locking on approval + Admin unlock with audit | ✅ |
| Quarterly check-in windows — DB-controlled, strictly enforced | ✅ |
| All 4 UoM scoring types (MIN / MAX / ZERO / TIMELINE) | ✅ |
| Shared goals with primary owner sync | ✅ |
| Append-only audit trail — APPROVE / RETURN / UNLOCK logged | ✅ |
| CSV / Excel export + real-time completion dashboard | ✅ |

---

## ⚡ Bonus Features Delivered

| Feature | Details |
|---|---|
| Escalation Engine | Configurable N-day rules · Vercel Cron runs daily at 9 AM |
| Email Notifications | 10 key events — submit, approve, return, unlock, escalate |
| Analytics Dashboard | QoQ trends · department heatmaps · manager effectiveness table |

---

## 💰 Cost

**$0 / month** — 100% free tiers

| Service | Usage | Cost |
|---|---|---|
| Vercel | Frontend hosting + Cron jobs | Free |
| Render | Backend API hosting | Free |
| Supabase | PostgreSQL database | Free |
| **Total** | | **$0/month** |

---

## 🎬 Judge Demo Path (8 minutes)

1. **Employee** (`prince@performx.com`) → Create goals → Submit for approval
2. **Manager** (`akshay@performx.com`) → Return one goal → Approve another
3. **Employee** → See returned badge → Revise → Resubmit
4. **Admin** (`pranul@performx.com`) → Audit logs → Export CSV → Manage cycles
5. **Employee** → Log quarterly actuals → See tracking scores auto-compute

---

## 📐 Architecture (one line)

```
Browser (Vercel) → FastAPI on Render → PostgreSQL on Supabase
                                     ↑
                        Vercel Cron (daily escalations)
```

---

*Built with ❤️ for AtomQuest Hackathon 1.0*
