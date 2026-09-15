import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.database import engine, Base, SessionLocal
from app.utils.seed_data import seed_database
from app.api import auth, documents, verification, templates, dashboard, demo

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed database on startup
try:
    db = SessionLocal()
    seed_database(db)
    db.close()
except Exception as e:
    print(f"Database seed notice: {e}")

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System",
    description="Authorized officer identity screening and reference template comparison platform",
    version="1.0.0"
)

# CORS configuration
is_production = os.getenv("ENVIRONMENT", "").lower() == "production"
frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
if is_production and not frontend_url:
    raise RuntimeError("FRONTEND_URL environment variable is required in production")

configured_origins = os.getenv("CORS_ORIGINS", "").split(",")
cors_origins = [
    origin.strip().rstrip("/")
    for origin in configured_origins
    if origin.strip()
]
if not is_production:
    cors_origins.extend(["http://localhost:5173", "http://127.0.0.1:5173"])
if frontend_url and frontend_url not in cors_origins:
    cors_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded documents, templates, overlays, and demo assets
os.makedirs("uploads", exist_ok=True)
os.makedirs(os.path.join("uploads", "documents"), exist_ok=True)
os.makedirs(os.path.join("uploads", "templates"), exist_ok=True)
os.makedirs(os.path.join("uploads", "demo_docs"), exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(verification.router, prefix="/api/verification", tags=["Verification"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo Mode"])

@app.get("/")
def root():
    return {
        "system": "AI-Based Fake Identity & Document Screening System",
        "status": "ONLINE",
        "demo_mode": True,
        "authoritative_verification": "SIMULATED / SANDBOX ONLY",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "screening-core-engine"}
