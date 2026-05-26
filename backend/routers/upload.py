"""
routers/upload.py
Handles CSV uploads for courses, rooms, and time slots.
Parses each file and stores the data in Supabase.
"""

import csv
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

from database import supabase
from models import UploadResponse

load_dotenv()

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")


# ─────────────────────────────────────────────
# JWT GUARD — protects all upload routes
# ─────────────────────────────────────────────

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ─────────────────────────────────────────────
# HELPER — parse uploaded CSV into list of dicts
# ─────────────────────────────────────────────

def parse_csv(file_bytes: bytes) -> list[dict]:
    content = file_bytes.decode("utf-8")
    reader  = csv.DictReader(io.StringIO(content))
    return [row for row in reader]


# ─────────────────────────────────────────────
# ROUTE — Upload all three CSVs at once
# ─────────────────────────────────────────────

@router.post("/", response_model=UploadResponse)
def upload_csvs(
    courses_file:   UploadFile = File(...),
    rooms_file:     UploadFile = File(...),
    slots_file:     UploadFile = File(...),
    admin:          str        = Depends(verify_token),
):
    """
    Accepts three CSV uploads: courses, rooms, time_slots.
    Clears existing data before inserting fresh records.
    Requires a valid JWT token.
    """

    # ── COURSES ───────────────────────────────
    courses_rows = parse_csv(courses_file.file.read())
    if not courses_rows:
        raise HTTPException(status_code=400, detail="courses CSV is empty")

    courses_data = []
    for row in courses_rows:
        try:
            courses_data.append({
                "course_code":    row["course_code"].strip(),
                "course_name":    row["course_name"].strip(),
                "department":     row["department"].strip().upper(),
                "level":          int(row["level"]),
                "enrolled_count": int(row["enrolled_count"]),
                "lecturer":       row["lecturer"].strip(),
            })
        except (KeyError, ValueError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid courses CSV format: {str(e)}"
            )

    # ── ROOMS ─────────────────────────────────
    rooms_rows = parse_csv(rooms_file.file.read())
    if not rooms_rows:
        raise HTTPException(status_code=400, detail="rooms CSV is empty")

    rooms_data = []
    for row in rooms_rows:
        try:
            rooms_data.append({
                "room_id":   row["room_id"].strip(),
                "room_name": row["room_name"].strip(),
                "building":  row["building"].strip(),
                "capacity":  int(row["capacity"]),
            })
        except (KeyError, ValueError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rooms CSV format: {str(e)}"
            )

    # ── TIME SLOTS ────────────────────────────
    slots_rows = parse_csv(slots_file.file.read())
    if not slots_rows:
        raise HTTPException(status_code=400, detail="time_slots CSV is empty")

    slots_data = []
    for row in slots_rows:
        try:
            slots_data.append({
                "slot_id":    int(row["slot_id"]),
                "week":       int(row["week"]) if "week" in row else 1,
                "day":        row["day"].strip(),
                "label":      row["label"].strip(),
                "start_time": row["start_time"].strip(),
                "end_time":   row["end_time"].strip(),
            })
        except (KeyError, ValueError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_slots CSV format: {str(e)}"
            )

    # ── CLEAR EXISTING DATA ───────────────────
    # Always wipe before inserting so re-uploads stay clean
    supabase.table("courses").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("rooms").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("time_slots").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("timetable").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("conflicts_log").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    # ── INSERT FRESH DATA ─────────────────────
    supabase.table("courses").insert(courses_data).execute()
    supabase.table("rooms").insert(rooms_data).execute()
    supabase.table("time_slots").insert(slots_data).execute()

    return UploadResponse(
        message="CSVs uploaded and stored successfully",
        courses_loaded=len(courses_data),
        rooms_loaded=len(rooms_data),
        slots_loaded=len(slots_data),
    )