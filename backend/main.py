"""
main.py
FastAPI entry point for the UCC Exam Timetable Generator.
All routers are registered here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import auth
app.include_router(auth.router, prefix="/auth", tags=["Auth"])


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