"""
models.py
Pydantic schemas for request/response validation across all routers.
"""

from pydantic import BaseModel
from typing import Optional


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_name: str


# ─────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────

class UploadResponse(BaseModel):
    message: str
    courses_loaded: int
    rooms_loaded: int
    slots_loaded: int


# ─────────────────────────────────────────────
# TIMETABLE
# ─────────────────────────────────────────────

class TimetableEntry(BaseModel):
    course_code: str
    course_name: str
    department: str
    level: int
    lecturer: str
    enrolled_count: int
    rooms_needed: int
    slot_id: int
    day: str
    label: str
    start_time: str
    end_time: str
    rooms_assigned: list[str]

class UnscheduledEntry(BaseModel):
    course_code: str
    course_name: str
    department: str
    level: int
    enrolled_count: int
    reason: str

class TimetableResponse(BaseModel):
    assignments: list[TimetableEntry]
    unscheduled: list[UnscheduledEntry]
    total_scheduled: int
    total_unscheduled: int
    message: str