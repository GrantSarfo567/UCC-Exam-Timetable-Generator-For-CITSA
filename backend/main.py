"""
main.py
FastAPI entry point for the UCC Exam Timetable Generator.
All routers are registered here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, upload, timetable

app = FastAPI(
    title="UCC Exam Timetable Generator",
    description="Automated exam timetable generation for CS and IT departments — University of Cape Coast",
    version="1.0.0",
)

# ─────────────────────────────────────────────
# CORS — allows the React frontend to talk to this API
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(timetable.router, prefix="/timetable", tags=["Timetable"])

# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "system": "UCC Exam Timetable Generator",
        "version": "1.0.0"
    }