"""
UCC Exam Timetable Scheduler
==============================
Algorithm: Greedy Graph Colouring

Core idea:
- Each course is a NODE in a graph
- Two courses share an EDGE if they conflict (same department + same level = same students)
- Each time slot is a COLOUR
- Goal: assign colours (slots) so no two connected nodes share a colour

This file is intentionally standalone — no FastAPI, no database.
Run it directly to verify the algorithm works before wiring it up to anything.

Author: Darks Technologies
Project: UCC Exam Timetable Generator
"""

import csv
import math
import random
from collections import defaultdict
from pprint import pprint


# ─────────────────────────────────────────────
# 1. DATA LOADING
# ─────────────────────────────────────────────

def load_courses(filepath: str) -> list[dict]:
    """
    Load courses from CSV.
    Expected columns: course_code, course_name, department, level,
                      enrolled_count, lecturer
    """
    courses = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            courses.append({
                "course_code":    row["course_code"].strip(),
                "course_name":    row["course_name"].strip(),
                "department":     row["department"].strip().upper(),
                "level":          int(row["level"]),
                "enrolled_count": int(row["enrolled_count"]),
                "lecturer":       row["lecturer"].strip(),
            })
    return courses


def load_rooms(filepath: str) -> list[dict]:
    """
    Load exam rooms from CSV.
    Expected columns: room_id, room_name, building, capacity
    """
    rooms = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rooms.append({
                "room_id":   row["room_id"].strip(),
                "room_name": row["room_name"].strip(),
                "building":  row["building"].strip(),
                "capacity":  int(row["capacity"]),
            })
    return rooms


def load_slots(filepath: str) -> list[dict]:
    """
    Load time slots from CSV.
    Expected columns: slot_id, week, day, label, start_time, end_time
    The 'week' column is optional — defaults to 1 if not present.
    """
    slots = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slots.append({
                "slot_id":    int(row["slot_id"]),
                "week":       int(row["week"]) if "week" in row else 1,
                "day":        row["day"].strip(),
                "label":      row["label"].strip(),
                "start_time": row["start_time"].strip(),
                "end_time":   row["end_time"].strip(),
            })
    return slots


# ─────────────────────────────────────────────
# 2. CONFLICT GROUP BUILDER
# ─────────────────────────────────────────────

def build_conflict_groups(courses: list[dict]) -> dict[tuple, list[str]]:
    """
    Group courses by (department, level).
    All courses in a group share the same students and CANNOT be
    scheduled in the same time slot.

    Returns:
        { ("CS", 100): ["CS101", "CS102", ...], ("IT", 200): [...], ... }
    """
    groups = defaultdict(list)
    for course in courses:
        key = (course["department"], course["level"])
        groups[key].append(course["course_code"])
    return dict(groups)


# ─────────────────────────────────────────────
# 3. CORE SCHEDULING ALGORITHM
# ─────────────────────────────────────────────

def rooms_needed(enrolled_count: int, room_capacity: int = 100) -> int:
    """
    Calculate how many rooms a course needs.
    e.g. 243 students / 100 capacity = ceil(2.43) = 3 rooms
    """
    return math.ceil(enrolled_count / room_capacity)


def schedule(
    courses: list[dict],
    rooms: list[dict],
    slots: list[dict],
    max_rooms_per_slot: int = 3,
) -> dict:
    """
    Main scheduling function.

    Strategy (Greedy Graph Colouring):
    1. Sort courses by enrolled_count DESC — hardest to place goes first.
       (Large courses need more rooms, so they are more constrained.)
    2. For each course:
       a. Find which slots are already blocked by its conflict group.
       b. Find the first slot that is NOT blocked, has enough free rooms,
          AND does not exceed max_rooms_per_slot for that slot.
       c. Assign that slot and mark those rooms as used.
    3. If no valid slot exists → log as unscheduled conflict.

    max_rooms_per_slot controls how many rooms can be occupied in a single
    slot. A lower value (e.g. 4) forces the algorithm to spread exams across
    more slots — producing a realistic month-long exam schedule rather than
    packing everything into the first two weeks.

    Returns:
        {
          "assignments": [ { course details + slot + rooms assigned } ],
          "unscheduled": [ { course details + reason } ],
          "slot_usage":  { slot_id: [room_ids in use] },
        }
    """

    # Build lookup maps for efficiency
    room_capacity = rooms[0]["capacity"]        # All rooms same capacity (100)
    all_room_ids  = [r["room_id"] for r in rooms]

    # course_code → its conflict group key
    course_to_group = {}
    for course in courses:
        key = (course["department"], course["level"])
        course_to_group[course["course_code"]] = key

    # Tracks which room_ids are occupied per slot_id
    # { slot_id: set(room_ids) }
    slot_rooms_used: dict[int, set] = defaultdict(set)

    # Tracks which slot_ids each conflict group has already used
    # { (dept, level): [slot_id, ...] }
    group_slot_assignments: dict[tuple, list[int]] = defaultdict(list)

    assignments = []
    unscheduled = []

    # Sort: most enrolled first (most constrained → schedule first)
    sorted_courses = sorted(courses, key=lambda c: c["enrolled_count"], reverse=True)

    for course in sorted_courses:
        code         = course["course_code"]
        group_key    = course_to_group[code]
        needed_rooms = rooms_needed(course["enrolled_count"], room_capacity)

        # Slots already used by any course in the same conflict group
        blocked_slots = set(group_slot_assignments[group_key])

        assigned = False

        for slot in slots:
            sid = slot["slot_id"]

            # Skip if this slot is blocked for this conflict group
            if sid in blocked_slots:
                continue

            # Enforce max rooms per slot — this is what spreads exams
            # across the full exam period instead of packing early slots
            rooms_used_in_slot = len(slot_rooms_used[sid])
            if rooms_used_in_slot + needed_rooms > max_rooms_per_slot:
                continue

            # Find rooms that are free in this slot
            free_rooms = [
                r for r in all_room_ids
                if r not in slot_rooms_used[sid]
            ]

            # Check if enough free rooms exist
            if len(free_rooms) < needed_rooms:
                continue

            # Valid slot found — assign it
            # Randomize room selection so all 10 rooms get used evenly
            chosen_rooms = random.sample(free_rooms, needed_rooms)

            # Mark rooms as occupied in this slot
            slot_rooms_used[sid].update(chosen_rooms)

            # Mark this slot as used by this conflict group
            group_slot_assignments[group_key].append(sid)

            assignments.append({
                "course_code":    code,
                "course_name":    course["course_name"],
                "department":     course["department"],
                "level":          course["level"],
                "lecturer":       course["lecturer"],
                "enrolled_count": course["enrolled_count"],
                "rooms_needed":   needed_rooms,
                "slot_id":        sid,
                "week":           slot.get("week", 1),
                "day":            slot["day"],
                "label":          slot["label"],
                "start_time":     slot["start_time"],
                "end_time":       slot["end_time"],
                "rooms_assigned": chosen_rooms,
            })

            assigned = True
            break  # Move to next course

        if not assigned:
            # No valid slot found for this course
            unscheduled.append({
                "course_code":    code,
                "course_name":    course["course_name"],
                "department":     course["department"],
                "level":          course["level"],
                "enrolled_count": course["enrolled_count"],
                "reason": (
                    f"No available slot with {needed_rooms} free room(s) "
                    f"outside conflict group {group_key}. "
                    f"Consider adding more time slots or increasing max_rooms_per_slot."
                ),
            })

    return {
        "assignments": assignments,
        "unscheduled": unscheduled,
        "slot_usage":  {k: list(v) for k, v in slot_rooms_used.items()},
    }


# ─────────────────────────────────────────────
# 4. RESULTS PRINTER (terminal verification)
# ─────────────────────────────────────────────

def print_timetable(result: dict, slots: list[dict]):
    """Pretty-print the generated timetable grouped by week, day and slot."""

    slot_map = {s["slot_id"]: s for s in slots}
    by_slot  = defaultdict(list)

    for a in result["assignments"]:
        by_slot[a["slot_id"]].append(a)

    print("\n" + "=" * 70)
    print("  UCC EXAM TIMETABLE — Computer Science & IT Department")
    print("=" * 70)

    current_week = None
    for sid in sorted(by_slot.keys()):
        slot    = slot_map[sid]
        courses = by_slot[sid]
        week    = slot.get("week", 1)

        if week != current_week:
            current_week = week
            print(f"\n{'─' * 70}")
            print(f"  WEEK {week}")
            print(f"{'─' * 70}")

        print(f"\n{slot['day'].upper()} | {slot['label']} | {slot['start_time']} – {slot['end_time']}")
        print("-" * 70)
        for c in sorted(courses, key=lambda x: (x["department"], x["level"])):
            rooms_str = ", ".join(c["rooms_assigned"])
            print(
                f"  [{c['department']} L{c['level']}]  "
                f"{c['course_code']} — {c['course_name']}\n"
                f"           Lecturer: {c['lecturer']} | "
                f"Students: {c['enrolled_count']} | "
                f"Rooms: {rooms_str}\n"
            )

    print("=" * 70)
    print(f"\nScheduled:   {len(result['assignments'])} courses")
    print(f"Unscheduled: {len(result['unscheduled'])} courses")

    if result["unscheduled"]:
        print("\n-- CONFLICT LOG --────────────────────────────────────────────")
        for u in result["unscheduled"]:
            print(f"  {u['course_code']} — {u['course_name']}")
            print(f"     Reason: {u['reason']}\n")


def print_summary(result: dict):
    """Print a quick slot utilisation summary."""
    print("\n-- SLOT UTILISATION ──────────────────────────────────────────")
    for sid, rooms in sorted(result["slot_usage"].items()):
        print(f"  Slot {sid:>2}: {len(rooms)} room(s) occupied — {rooms}")
    print()


# ─────────────────────────────────────────────
# 5. ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Load data
    courses = load_courses("data/courses.csv")
    rooms   = load_rooms("data/rooms.csv")
    slots   = load_slots("data/time_slots.csv")

    print(f"\nLoaded {len(courses)} courses, {len(rooms)} rooms, {len(slots)} slots.")

    # Run algorithm — max 3 rooms per slot spreads across full exam period
    result = schedule(courses, rooms, slots, max_rooms_per_slot=3)

    # Print full timetable
    print_timetable(result, slots)

    # Print slot utilisation
    print_summary(result)