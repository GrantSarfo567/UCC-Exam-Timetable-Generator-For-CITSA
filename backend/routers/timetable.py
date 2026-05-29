"""
routers/timetable.py
Fetches courses, rooms, and slots from Supabase,
runs the scheduling algorithm, persists results,
and returns the full timetable.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

from database import supabase
from models import TimetableResponse
from scheduler import schedule

load_dotenv()

router   = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")


# ─────────────────────────────────────────────
# JWT GUARD
# ─────────────────────────────────────────────

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload  = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ─────────────────────────────────────────────
# ROUTE — Generate timetable
# ─────────────────────────────────────────────

@router.post("/generate", response_model=TimetableResponse)
def generate_timetable(admin: str = Depends(verify_token)):
    """
    Reads courses, rooms, and time slots from Supabase,
    runs the greedy graph colouring scheduler,
    saves results to timetable and conflicts_log tables,
    and returns the full timetable.
    """

    # ── FETCH DATA FROM SUPABASE ──────────────
    courses_res = supabase.table("courses").select("*").execute()
    rooms_res   = supabase.table("rooms").select("*").execute()
    slots_res   = supabase.table("time_slots").select("*").order("slot_id").execute()

    if not courses_res.data:
        raise HTTPException(status_code=400, detail="No courses found. Please upload CSVs first.")
    if not rooms_res.data:
        raise HTTPException(status_code=400, detail="No rooms found. Please upload CSVs first.")
    if not slots_res.data:
        raise HTTPException(status_code=400, detail="No time slots found. Please upload CSVs first.")

    # ── RUN SCHEDULER ─────────────────────────
    result = schedule(
        courses=courses_res.data,
        rooms=rooms_res.data,
        slots=slots_res.data,
    )

    assignments = result["assignments"]
    unscheduled = result["unscheduled"]

    # ── CLEAR PREVIOUS RESULTS ────────────────
    supabase.table("timetable").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("conflicts_log").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    # ── SAVE TIMETABLE ────────────────────────
    if assignments:
        timetable_rows = [
            {
                "course_code":    a["course_code"],
                "course_name":    a["course_name"],
                "department":     a["department"],
                "level":          a["level"],
                "lecturer":       a["lecturer"],
                "enrolled_count": a["enrolled_count"],
                "rooms_needed":   a["rooms_needed"],
                "slot_id":        a["slot_id"],
                "day":            a["day"],
                "label":          a["label"],
                "start_time":     a["start_time"],
                "end_time":       a["end_time"],
                "rooms_assigned": a["rooms_assigned"],
            }
            for a in assignments
        ]
        supabase.table("timetable").insert(timetable_rows).execute()

    # ── SAVE CONFLICTS LOG ────────────────────
    if unscheduled:
        conflict_rows = [
            {
                "course_code":    u["course_code"],
                "course_name":    u["course_name"],
                "department":     u["department"],
                "level":          u["level"],
                "enrolled_count": u["enrolled_count"],
                "reason":         u["reason"],
            }
            for u in unscheduled
        ]
        supabase.table("conflicts_log").insert(conflict_rows).execute()

    return TimetableResponse(
        assignments=assignments,
        unscheduled=unscheduled,
        total_scheduled=len(assignments),
        total_unscheduled=len(unscheduled),
        message=f"Timetable generated: {len(assignments)} scheduled, {len(unscheduled)} unscheduled."
    )


# ─────────────────────────────────────────────
# ROUTE — Fetch saved timetable
# ─────────────────────────────────────────────

@router.get("/", response_model=TimetableResponse)
def get_timetable(admin: str = Depends(verify_token)):
    """
    Returns the most recently generated timetable from Supabase.
    """
    timetable_res  = supabase.table("timetable").select("*").order("slot_id").execute()
    conflicts_res  = supabase.table("conflicts_log").select("*").execute()

    assignments = timetable_res.data or []
    unscheduled = conflicts_res.data or []

    if not assignments:
        raise HTTPException(
            status_code=404,
            detail="No timetable found. Please generate one first."
        )

    return TimetableResponse(
        assignments=assignments,
        unscheduled=unscheduled,
        total_scheduled=len(assignments),
        total_unscheduled=len(unscheduled),
        message=f"Timetable retrieved: {len(assignments)} scheduled, {len(unscheduled)} unscheduled."
    )