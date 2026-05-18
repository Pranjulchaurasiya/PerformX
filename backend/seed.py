"""
PerformX seed script — creates demo data for all 3 roles.

Run: python seed.py

Demo credentials:
  Admin:    pranul@performx.com      / Admin@123
  Manager:  akshay@performx.com      / Manager@123
  Manager:  saandeep@performx.com    / Manager@123
  Employee: prince@performx.com      / Employee@123  (goals locked, Q1 actuals logged)
  Employee: anshul@performx.com      / Employee@123  (goals submitted — pending approval)
  Employee: vinayak@performx.com     / Employee@123  (goals returned for rework)
  Employee: abhishek@performx.com    / Employee@123  (goals locked)
  Employee: sarthak@performx.com     / Employee@123  (goals draft)
  Employee: prachi@performx.com      / Employee@123  (goals locked, Q1 actuals logged)
  Employee: priyanshoo@performx.com  / Employee@123  (goals submitted)
  Employee: nidhi@performx.com       / Employee@123  (goals locked)
  Employee: prashant@performx.com    / Employee@123  (goals draft)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.thrust_area import ThrustArea
from app.models.goal_cycle import GoalCycle, CyclePhase
from app.models.goal import Goal, GoalStatus, UoMType
from app.models.achievement import Achievement, GoalProgressStatus
from app.models.checkin import Checkin, CommentType
from app.models.escalation import EscalationRule
import app.models  # noqa — register all models

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed():
    if db.query(Department).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    # ── Departments ───────────────────────────────────────────────────────────
    sales   = Department(name="Sales")
    engg    = Department(name="Engineering")
    hr      = Department(name="Human Resources")
    ops     = Department(name="Operations")
    db.add_all([sales, engg, hr, ops])
    db.flush()

    # ── Thrust Areas ──────────────────────────────────────────────────────────
    ta_revenue  = ThrustArea(name="Revenue Growth",         department_id=sales.id)
    ta_quality  = ThrustArea(name="Product Quality",        department_id=engg.id)
    ta_people   = ThrustArea(name="People Development",     department_id=hr.id)
    ta_ops      = ThrustArea(name="Operational Excellence", department_id=ops.id)
    ta_customer = ThrustArea(name="Customer Success",       department_id=sales.id)
    db.add_all([ta_revenue, ta_quality, ta_people, ta_ops, ta_customer])
    db.flush()

    # ── Admin ─────────────────────────────────────────────────────────────────
    pranul = User(
        name="Pranul Sharma",
        email="pranul@performx.com",
        hashed_password=get_password_hash("Admin@123"),
        role=UserRole.admin,
        department_id=hr.id,
    )
    db.add(pranul)
    db.flush()

    # ── Managers ─────────────────────────────────────────────────────────────
    akshay = User(
        name="Akshay Verma",
        email="akshay@performx.com",
        hashed_password=get_password_hash("Manager@123"),
        role=UserRole.manager,
        department_id=sales.id,
        manager_id=pranul.id,
    )
    saandeep = User(
        name="Saandeep Gupta",
        email="saandeep@performx.com",
        hashed_password=get_password_hash("Manager@123"),
        role=UserRole.manager,
        department_id=engg.id,
        manager_id=pranul.id,
    )
    db.add_all([akshay, saandeep])
    db.flush()

    # ── Employees under Akshay (Sales) ────────────────────────────────────────
    prince = User(
        name="Prince Rajput",
        email="prince@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=sales.id,
        manager_id=akshay.id,
    )
    anshul = User(
        name="Anshul Tiwari",
        email="anshul@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=sales.id,
        manager_id=akshay.id,
    )
    vinayak = User(
        name="Vinayak Mishra",
        email="vinayak@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=sales.id,
        manager_id=akshay.id,
    )
    abhishek = User(
        name="Abhishek Pandey",
        email="abhishek@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=sales.id,
        manager_id=akshay.id,
    )
    sarthak = User(
        name="Sarthak Joshi",
        email="sarthak@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=sales.id,
        manager_id=akshay.id,
    )
    db.add_all([prince, anshul, vinayak, abhishek, sarthak])
    db.flush()

    # ── Employees under Saandeep (Engineering) ────────────────────────────────
    prachi = User(
        name="Prachi Agarwal",
        email="prachi@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=engg.id,
        manager_id=saandeep.id,
    )
    priyanshoo = User(
        name="Priyanshoo Singh",
        email="priyanshoo@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=engg.id,
        manager_id=saandeep.id,
    )
    nidhi = User(
        name="Nidhi Saxena",
        email="nidhi@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=engg.id,
        manager_id=saandeep.id,
    )
    prashant = User(
        name="Prashant Kumar",
        email="prashant@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=engg.id,
        manager_id=saandeep.id,
    )
    db.add_all([prachi, priyanshoo, nidhi, prashant])
    db.flush()

    # ── Test Employee (Fresh — zero goals) ────────────────────────────────────
    test_emp = User(
        name="Test Employee",
        email="test@performx.com",
        hashed_password=get_password_hash("Employee@123"),
        role=UserRole.employee,
        department_id=sales.id,
        manager_id=akshay.id,
    )
    db.add(test_emp)
    db.flush()

    # ── Goal Cycles ───────────────────────────────────────────────────────────
    today = date.today()
    year  = today.year
    yy    = str(year + 1)[-2:]

    cycle_gs = GoalCycle(name=f"FY {year}-{yy} Goal Setting", phase=CyclePhase.goal_setting,
                         window_open=date(year, 5, 1),  window_close=date(year, 5, 31),  is_active=False, penalty_factor=0.05)
    cycle_q1 = GoalCycle(name=f"FY {year}-{yy} Q1",           phase=CyclePhase.q1,
                         window_open=date(year, 7, 1),  window_close=date(year, 7, 31),  is_active=True,  penalty_factor=0.05)
    cycle_q2 = GoalCycle(name=f"FY {year}-{yy} Q2",           phase=CyclePhase.q2,
                         window_open=date(year, 10, 1), window_close=date(year, 10, 31), is_active=False, penalty_factor=0.05)
    cycle_q3 = GoalCycle(name=f"FY {year}-{yy} Q3",           phase=CyclePhase.q3,
                         window_open=date(year+1, 1, 1),window_close=date(year+1, 1, 31),is_active=False, penalty_factor=0.05)
    cycle_q4 = GoalCycle(name=f"FY {year}-{yy} Q4",           phase=CyclePhase.q4,
                         window_open=date(year+1, 3, 1),window_close=date(year+1, 4, 30),is_active=False, penalty_factor=0.05)
    db.add_all([cycle_gs, cycle_q1, cycle_q2, cycle_q3, cycle_q4])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # PRINCE — 4 LOCKED goals + Q1 achievements (demo-ready)
    # ══════════════════════════════════════════════════════════════════════════
    pg1 = Goal(employee_id=prince.id, thrust_area_id=ta_revenue.id,
               title="Achieve Q1 Sales Target",
               description="Hit ₹50L in new business revenue for Q1",
               uom_type=UoMType.min, target=5000000.0, weightage=40.0, status=GoalStatus.locked)
    pg2 = Goal(employee_id=prince.id, thrust_area_id=ta_ops.id,
               title="Reduce Customer Response TAT",
               description="Reduce average response time from 48h to 24h",
               uom_type=UoMType.max, target=24.0, weightage=30.0, status=GoalStatus.locked)
    pg3 = Goal(employee_id=prince.id, thrust_area_id=ta_ops.id,
               title="Zero Safety Incidents",
               description="Maintain zero workplace safety incidents",
               uom_type=UoMType.zero, weightage=15.0, status=GoalStatus.locked)
    pg4 = Goal(employee_id=prince.id, thrust_area_id=ta_people.id,
               title="Complete Leadership Certification",
               description="Complete L2 leadership certification program",
               uom_type=UoMType.timeline, target_date=date(year, 9, 30),
               weightage=15.0, status=GoalStatus.locked)
    db.add_all([pg1, pg2, pg3, pg4])
    db.flush()

    db.add_all([
        Achievement(goal_id=pg1.id, cycle_id=cycle_q1.id, actual_value=3200000.0,
                    tracking_score=64.0, goal_status=GoalProgressStatus.on_track),
        Achievement(goal_id=pg2.id, cycle_id=cycle_q1.id, actual_value=28.0,
                    tracking_score=round(24/28*100, 2), goal_status=GoalProgressStatus.on_track),
        Achievement(goal_id=pg3.id, cycle_id=cycle_q1.id, actual_value=0.0,
                    tracking_score=100.0, goal_status=GoalProgressStatus.on_track),
    ])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # ANSHUL — 3 SUBMITTED goals (pending Akshay's approval)
    # ══════════════════════════════════════════════════════════════════════════
    ag1 = Goal(employee_id=anshul.id, thrust_area_id=ta_revenue.id,
               title="New Enterprise Client Acquisition",
               description="Acquire 10 new enterprise clients in FY",
               uom_type=UoMType.min, target=10.0, weightage=50.0, status=GoalStatus.submitted)
    ag2 = Goal(employee_id=anshul.id, thrust_area_id=ta_customer.id,
               title="Improve Pipeline Conversion Rate",
               description="Improve conversion from 20% to 30%",
               uom_type=UoMType.min, target=30.0, weightage=30.0, status=GoalStatus.submitted)
    ag3 = Goal(employee_id=anshul.id, thrust_area_id=ta_people.id,
               title="Complete Salesforce Certification",
               description="Obtain Salesforce Advanced Admin certification",
               uom_type=UoMType.timeline, target_date=date(year, 8, 31),
               weightage=20.0, status=GoalStatus.submitted)
    db.add_all([ag1, ag2, ag3])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # VINAYAK — 3 RETURNED goals (needs rework)
    # ══════════════════════════════════════════════════════════════════════════
    vg1 = Goal(employee_id=vinayak.id, thrust_area_id=ta_revenue.id,
               title="Upsell Existing Accounts",
               description="Increase revenue from existing accounts by 20%",
               uom_type=UoMType.min, target=20.0, weightage=50.0, status=GoalStatus.returned,
               rework_comment="Please increase the target to 25% and add a description of the strategy.")
    vg2 = Goal(employee_id=vinayak.id, thrust_area_id=ta_customer.id,
               title="Improve NPS Score",
               description="Improve Net Promoter Score from 40 to 60",
               uom_type=UoMType.min, target=60.0, weightage=30.0, status=GoalStatus.returned,
               rework_comment="Clarify how NPS will be measured — which survey tool?")
    vg3 = Goal(employee_id=vinayak.id, thrust_area_id=ta_people.id,
               title="Attend Product Training",
               description="Complete all mandatory product training modules",
               uom_type=UoMType.timeline, target_date=date(year, 7, 31),
               weightage=20.0, status=GoalStatus.returned,
               rework_comment="Deadline seems too early — please revise to September.")
    db.add_all([vg1, vg2, vg3])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # ABHISHEK — 4 LOCKED goals
    # ══════════════════════════════════════════════════════════════════════════
    abg1 = Goal(employee_id=abhishek.id, thrust_area_id=ta_revenue.id,
                title="Achieve Annual Revenue Target",
                description="Hit ₹1Cr in annual revenue",
                uom_type=UoMType.min, target=10000000.0, weightage=40.0, status=GoalStatus.locked)
    abg2 = Goal(employee_id=abhishek.id, thrust_area_id=ta_customer.id,
                title="Maintain Customer Retention Rate",
                description="Keep churn below 5%",
                uom_type=UoMType.max, target=5.0, weightage=30.0, status=GoalStatus.locked)
    abg3 = Goal(employee_id=abhishek.id, thrust_area_id=ta_ops.id,
                title="Zero Escalations from Key Accounts",
                description="No escalations from top 10 accounts",
                uom_type=UoMType.zero, weightage=15.0, status=GoalStatus.locked)
    abg4 = Goal(employee_id=abhishek.id, thrust_area_id=ta_people.id,
                title="Complete CRM Advanced Training",
                description="Finish CRM advanced module by Q2",
                uom_type=UoMType.timeline, target_date=date(year, 10, 31),
                weightage=15.0, status=GoalStatus.locked)
    db.add_all([abg1, abg2, abg3, abg4])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # SARTHAK — 2 DRAFT goals (not yet submitted)
    # ══════════════════════════════════════════════════════════════════════════
    sg1 = Goal(employee_id=sarthak.id, thrust_area_id=ta_revenue.id,
               title="Generate New Leads",
               description="Generate 200 qualified leads per quarter",
               uom_type=UoMType.min, target=200.0, weightage=60.0, status=GoalStatus.draft)
    sg2 = Goal(employee_id=sarthak.id, thrust_area_id=ta_people.id,
               title="Complete Onboarding Program",
               description="Finish all onboarding modules within 30 days",
               uom_type=UoMType.timeline, target_date=date(year, 6, 30),
               weightage=40.0, status=GoalStatus.draft)
    db.add_all([sg1, sg2])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # PRACHI — 4 LOCKED goals + Q1 achievements (Engineering)
    # ══════════════════════════════════════════════════════════════════════════
    prg1 = Goal(employee_id=prachi.id, thrust_area_id=ta_quality.id,
                title="Reduce Bug Escape Rate",
                description="Reduce production bugs by 40%",
                uom_type=UoMType.max, target=10.0, weightage=35.0, status=GoalStatus.locked)
    prg2 = Goal(employee_id=prachi.id, thrust_area_id=ta_quality.id,
                title="Achieve 90% Test Coverage",
                description="Increase unit test coverage to 90%",
                uom_type=UoMType.min, target=90.0, weightage=35.0, status=GoalStatus.locked)
    prg3 = Goal(employee_id=prachi.id, thrust_area_id=ta_ops.id,
                title="Zero Critical Incidents",
                description="No P0/P1 incidents caused by team",
                uom_type=UoMType.zero, weightage=15.0, status=GoalStatus.locked)
    prg4 = Goal(employee_id=prachi.id, thrust_area_id=ta_people.id,
                title="Complete AWS Certification",
                description="Obtain AWS Solutions Architect Associate",
                uom_type=UoMType.timeline, target_date=date(year, 11, 30),
                weightage=15.0, status=GoalStatus.locked)
    db.add_all([prg1, prg2, prg3, prg4])
    db.flush()

    db.add_all([
        Achievement(goal_id=prg1.id, cycle_id=cycle_q1.id, actual_value=8.0,
                    tracking_score=round(10/8*100, 2), goal_status=GoalProgressStatus.on_track),
        Achievement(goal_id=prg2.id, cycle_id=cycle_q1.id, actual_value=78.0,
                    tracking_score=round(78/90*100, 2), goal_status=GoalProgressStatus.on_track),
        Achievement(goal_id=prg3.id, cycle_id=cycle_q1.id, actual_value=0.0,
                    tracking_score=100.0, goal_status=GoalProgressStatus.on_track),
    ])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # PRIYANSHOO — 3 SUBMITTED goals (pending Saandeep's approval)
    # ══════════════════════════════════════════════════════════════════════════
    psg1 = Goal(employee_id=priyanshoo.id, thrust_area_id=ta_quality.id,
                title="Reduce API Response Time",
                description="Bring P95 latency below 200ms",
                uom_type=UoMType.max, target=200.0, weightage=40.0, status=GoalStatus.submitted)
    psg2 = Goal(employee_id=priyanshoo.id, thrust_area_id=ta_quality.id,
                title="Improve Code Review Coverage",
                description="Ensure 100% PRs reviewed before merge",
                uom_type=UoMType.min, target=100.0, weightage=35.0, status=GoalStatus.submitted)
    psg3 = Goal(employee_id=priyanshoo.id, thrust_area_id=ta_people.id,
                title="Complete System Design Course",
                description="Finish Grokking System Design course",
                uom_type=UoMType.timeline, target_date=date(year, 9, 30),
                weightage=25.0, status=GoalStatus.submitted)
    db.add_all([psg1, psg2, psg3])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # NIDHI — 4 LOCKED goals
    # ══════════════════════════════════════════════════════════════════════════
    ng1 = Goal(employee_id=nidhi.id, thrust_area_id=ta_quality.id,
               title="Achieve Sprint Velocity Target",
               description="Maintain average sprint velocity of 40 points",
               uom_type=UoMType.min, target=40.0, weightage=40.0, status=GoalStatus.locked)
    ng2 = Goal(employee_id=nidhi.id, thrust_area_id=ta_ops.id,
               title="Reduce Deployment Failures",
               description="Keep deployment failure rate below 2%",
               uom_type=UoMType.max, target=2.0, weightage=30.0, status=GoalStatus.locked)
    ng3 = Goal(employee_id=nidhi.id, thrust_area_id=ta_ops.id,
               title="Zero Security Vulnerabilities",
               description="No critical CVEs in production",
               uom_type=UoMType.zero, weightage=15.0, status=GoalStatus.locked)
    ng4 = Goal(employee_id=nidhi.id, thrust_area_id=ta_people.id,
               title="Complete Kubernetes Certification",
               description="Obtain CKA certification",
               uom_type=UoMType.timeline, target_date=date(year, 12, 31),
               weightage=15.0, status=GoalStatus.locked)
    db.add_all([ng1, ng2, ng3, ng4])
    db.flush()

    # ══════════════════════════════════════════════════════════════════════════
    # PRASHANT — 2 DRAFT goals
    # ══════════════════════════════════════════════════════════════════════════
    prsg1 = Goal(employee_id=prashant.id, thrust_area_id=ta_quality.id,
                 title="Implement Automated Testing Pipeline",
                 description="Set up CI/CD with automated test gates",
                 uom_type=UoMType.timeline, target_date=date(year, 8, 31),
                 weightage=50.0, status=GoalStatus.draft)
    prsg2 = Goal(employee_id=prashant.id, thrust_area_id=ta_ops.id,
                 title="Reduce Technical Debt",
                 description="Resolve 80% of existing tech debt tickets",
                 uom_type=UoMType.min, target=80.0, weightage=50.0, status=GoalStatus.draft)
    db.add_all([prsg1, prsg2])
    db.flush()

    # ── Manager Check-ins ─────────────────────────────────────────────────────
    db.add_all([
        Checkin(manager_id=akshay.id, employee_id=prince.id, cycle_id=cycle_q1.id,
                comment_type=CommentType.positive_feedback,
                comment_text="Prince is making excellent progress on revenue targets. "
                             "TAT reduction needs more focus in Q2.",
                is_completed=True),
        Checkin(manager_id=saandeep.id, employee_id=prachi.id, cycle_id=cycle_q1.id,
                comment_type=CommentType.positive_feedback,
                comment_text="Prachi has shown strong improvement in test coverage. "
                             "Keep up the momentum on bug reduction.",
                is_completed=True),
    ])
    db.flush()

    # ── Escalation Rules ──────────────────────────────────────────────────────
    db.add_all([
        EscalationRule(rule_name="Goal Not Submitted",      trigger_event="GOAL_NOT_SUBMITTED",
                       threshold_days=7,  step1_delay_days=3, step2_delay_days=5, is_active=True),
        EscalationRule(rule_name="Approval Pending Too Long", trigger_event="APPROVAL_PENDING",
                       threshold_days=5,  step1_delay_days=2, step2_delay_days=3, is_active=True),
        EscalationRule(rule_name="Check-in Overdue",        trigger_event="CHECKIN_OVERDUE",
                       threshold_days=10, step1_delay_days=3, step2_delay_days=5, is_active=True),
    ])

    db.commit()
    print("✓ Seed complete!")
    print()
    print("Demo credentials:")
    print("  Admin:    pranul@performx.com      / Admin@123")
    print("  Manager:  akshay@performx.com      / Manager@123   (Sales team)")
    print("  Manager:  saandeep@performx.com    / Manager@123   (Engineering team)")
    print()
    print("  Employees (Sales — under Akshay):")
    print("    prince@performx.com      / Employee@123  — 4 locked goals, Q1 actuals done")
    print("    anshul@performx.com      / Employee@123  — 3 submitted, pending approval")
    print("    vinayak@performx.com     / Employee@123  — 3 returned for rework")
    print("    abhishek@performx.com    / Employee@123  — 4 locked goals")
    print("    sarthak@performx.com     / Employee@123  — 2 draft goals")
    print("    test@performx.com        / Employee@123  — fresh account, zero goals")
    print()
    print("  Employees (Engineering — under Saandeep):")
    print("    prachi@performx.com      / Employee@123  — 4 locked goals, Q1 actuals done")
    print("    priyanshoo@performx.com  / Employee@123  — 3 submitted, pending approval")
    print("    nidhi@performx.com       / Employee@123  — 4 locked goals")
    print("    prashant@performx.com    / Employee@123  — 2 draft goals")
    db.close()


if __name__ == "__main__":
    seed()
