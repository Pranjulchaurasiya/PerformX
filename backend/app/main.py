"""
PerformX — Goal Setting & Progress Tracking Portal
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import Base, engine

# Import all models so SQLAlchemy registers them before create_all
from app.models import (  # noqa: F401
    user, department, thrust_area, goal, goal_cycle,
    achievement, checkin, audit_log, escalation,
    notification, shared_goal_link,
)

from app.routers import (
    auth, goals, achievements, checkins, admin,
    analytics, audit, reports, shared_goals, escalations,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Always create tables on startup — create_all is idempotent
    # (only creates tables that don't already exist)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="PerformX API",
    description="Goal Setting & Progress Tracking Portal",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS — allow frontend origins (dev + production)
# APP_BASE_URL should be set to your Vercel URL in production
allowed_origins = [
    settings.APP_BASE_URL,
    "http://localhost:5173",
    "http://localhost:3000",
]
# Also allow any *.vercel.app subdomain for preview deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(achievements.router, prefix="/api")
app.include_router(checkins.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(shared_goals.router, prefix="/api")
app.include_router(escalations.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "PerformX API"}


@app.post("/api/add-test-user")
def add_test_user(secret: str):
    """One-time endpoint to add test@performx.com. Remove after use."""
    if secret != "performx-seed-2024":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Forbidden")
    from app.core.database import SessionLocal
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "test@performx.com").first():
            return {"status": "already exists"}
        manager = db.query(User).filter(User.email == "akshay@performx.com").first()
        from app.models.department import Department
        sales = db.query(Department).filter(Department.name == "Sales").first()
        test_emp = User(
            name="Test Employee",
            email="test@performx.com",
            hashed_password=get_password_hash("Employee@123"),
            role=UserRole.employee,
            department_id=sales.id,
            manager_id=manager.id,
        )
        db.add(test_emp)
        db.commit()
        return {"status": "created", "email": "test@performx.com"}
    finally:
        db.close()
