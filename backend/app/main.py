from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .database import Base, engine, SessionLocal
from .models import *
from .routes import issues, analytics, auth
from .services import AIIssueDetector
from .services.auth import hash_password

# Get CORS origins from environment or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
cors_origins = [origin.strip() for origin in cors_origins]

# Create tables
Base.metadata.create_all(bind=engine)

# Create sample authority user on startup
def create_sample_authority():
    db = SessionLocal()
    try:
        # Check if admin already exists
        try:
            admin = db.query(User).filter(User.email == "admin@authority.com").first()
            if not admin:
                hashed_pwd = hash_password("admin123")
                admin_user = User(
                    email="admin@authority.com",
                    username="admin",
                    full_name="Authority Admin",
                    password_hash=hashed_pwd,
                    is_authority=True
                )
                db.add(admin_user)
                db.commit()
                print("✓ Sample authority user created: admin@authority.com / admin123")
        except Exception as e:
            print(f"Note: Could not create sample authority user on startup: {str(e)}")
            db.rollback()
    finally:
        db.close()

create_sample_authority()

app = FastAPI(
    title="Local Problem Reporter API",
    description="AI-powered platform for reporting and managing local infrastructure issues",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(issues.router)
app.include_router(analytics.router)

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Local Problem Reporter API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/system/info")
async def system_info():
    """Get system information"""
    detector = AIIssueDetector()
    return {
        "api_version": "1.0.0",
        "ai_model": detector.get_model_info(),
        "issue_categories": [
            "road_damage",
            "garbage",
            "water_leak",
            "traffic",
            "construction",
            "landslide",
            "other"
        ],
        "priority_levels": ["critical", "high", "medium", "low"]
    }


@app.get("/api/scoring-info")
async def get_scoring_info():
    """Get priority scoring system information"""
    from .services import PriorityScorer
    return PriorityScorer.get_scoring_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
