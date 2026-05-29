import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { getTimetable } from "../services/api"
import uccLogo from "../assets/ucc_logo.png"

const DAYS   = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
const LABELS = ["Morning", "Afternoon"]

export default function Timetable() {
  const navigate  = useNavigate()
  const adminName = localStorage.getItem("admin_name") || "Admin"

  const [data,        setData]        = useState(null)
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState("")
  const [activeWeek,  setActiveWeek]  = useState(1)
  const [filterDept,  setFilterDept]  = useState("ALL")
  const [filterLevel, setFilterLevel] = useState("ALL")

  useEffect(() => { fetchTimetable() }, [])

  const fetchTimetable = async () => {
    try {
      const res = await getTimetable()
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load timetable.")
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("admin_name")
    navigate("/login")
  }

  // Derive week from slot_id: 1-10 = week 1, 11-20 = week 2
  const getWeek = (slot_id) => Math.ceil(slot_id / 10)

  const filtered = data?.assignments?.filter(a => {
    const weekMatch  = getWeek(a.slot_id) === activeWeek
    const deptMatch  = filterDept  === "ALL" || a.department === filterDept
    const levelMatch = filterLevel === "ALL" || a.level === parseInt(filterLevel)
    return weekMatch && deptMatch && levelMatch
  }) || []

  const getCell = (day, label) =>
    filtered.filter(a => a.day === day && a.label === label)

  const deptCard  = (dept) => dept === "CS"
    ? "border-blue-200 bg-blue-50"
    : "border-red-200 bg-red-50"

  const deptBadge = (dept) => dept === "CS"
    ? "bg-blue-100 text-blue-800"
    : "bg-red-100 text-red-800"

  const deptText  = (dept) => dept === "CS"
    ? "text-blue-900"
    : "text-red-900"

  if (loading) return (
    <div className="min-h-screen bg-ucc-gray flex items-center justify-center">
      <p className="text-ucc-blue text-sm font-medium">Loading timetable...</p>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-ucc-gray flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-600 text-sm mb-3">{error}</p>
        <button onClick={() => navigate("/upload")}
          className="text-sm text-ucc-blue hover:underline">
          Go back to upload
        </button>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-ucc-gray">
      <div className="h-1 w-full bg-ucc-blue fixed top-0 left-0 z-50 print:hidden" />

      {/* Navbar */}
      <nav className="bg-white border-b border-ucc-border px-6 py-3 flex items-center justify-between print:hidden">
        <div className="flex items-center gap-3">
          <img src={uccLogo} alt="UCC Logo" className="w-9 h-9 object-contain" />
          <div>
            <p className="text-ucc-blue font-semibold text-sm leading-tight">
              University of Cape Coast
            </p>
            <p className="text-ucc-muted text-xs">Exam Timetable Generator</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/upload")}
            className="text-sm text-ucc-blue hover:underline"
          >
            Upload New
          </button>
          <button
            onClick={() => window.print()}
            className="text-sm bg-ucc-red hover:bg-red-700 text-white px-4 py-1.5 rounded-lg transition-colors"
          >
            Export PDF
          </button>
          <span className="text-ucc-muted text-sm">|</span>
          <span className="text-ucc-muted text-sm">{adminName}</span>
          <button onClick={handleLogout} className="text-sm text-ucc-red hover:underline">
            Logout
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8 print:px-2 print:py-2">

        {/* Print header — only shows when printing */}
        <div className="hidden print:block mb-6 text-center border-b border-gray-300 pb-4">
          <img src={uccLogo} alt="UCC Logo" className="w-16 h-16 object-contain mx-auto mb-2" />
          <h1 className="text-lg font-bold text-ucc-blue">University of Cape Coast</h1>
          <p className="text-sm text-gray-600">Management Information System</p>
          <p className="text-sm font-semibold mt-1">
            Computer Science & IT Department — Exam Timetable
          </p>
        </div>

        {/* Page header */}
        <div className="mb-6 print:hidden">
          <h1 className="text-ucc-blue text-2xl font-semibold">Exam Timetable</h1>
          <p className="text-ucc-muted text-sm mt-1">
            Computer Science & Information Technology — L100 to L400
          </p>
          <div className="w-12 h-0.5 bg-ucc-red rounded-full mt-3" />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6 print:hidden">
          <div className="bg-white border border-ucc-border rounded-xl p-4">
            <p className="text-ucc-muted text-xs mb-1">Total Scheduled</p>
            <p className="text-ucc-blue text-2xl font-semibold">{data?.total_scheduled}</p>
          </div>
          <div className="bg-white border border-ucc-border rounded-xl p-4">
            <p className="text-ucc-muted text-xs mb-1">Unscheduled</p>
            <p className={`text-2xl font-semibold ${data?.total_unscheduled > 0 ? "text-ucc-red" : "text-ucc-blue"}`}>
              {data?.total_unscheduled}
            </p>
          </div>
          <div className="bg-white border border-ucc-border rounded-xl p-4">
            <p className="text-ucc-muted text-xs mb-1">Exam Period</p>
            <p className="text-ucc-blue text-2xl font-semibold">4 Weeks</p>
          </div>
        </div>

        {/* Week tabs + Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4 print:hidden">
          <div className="flex gap-2">
            {[1, 2, 3, 4].map(w => (
              <button
                key={w}
                onClick={() => setActiveWeek(w)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  activeWeek === w
                    ? "bg-ucc-blue text-white"
                    : "bg-white border border-ucc-border text-ucc-muted hover:text-ucc-blue"
                }`}
              >
                Week {w}
              </button>
            ))}
          </div>

          <div className="flex gap-3">
            <select
              value={filterDept}
              onChange={e => setFilterDept(e.target.value)}
              className="text-sm border border-ucc-border rounded-lg px-3 py-1.5 text-ucc-text bg-white focus:outline-none focus:border-ucc-blue"
            >
              <option value="ALL">All Departments</option>
              <option value="CS">Computer Science</option>
              <option value="IT">Information Technology</option>
            </select>

            <select
              value={filterLevel}
              onChange={e => setFilterLevel(e.target.value)}
              className="text-sm border border-ucc-border rounded-lg px-3 py-1.5 text-ucc-text bg-white focus:outline-none focus:border-ucc-blue"
            >
              <option value="ALL">All Levels</option>
              <option value="100">Level 100</option>
              <option value="200">Level 200</option>
              <option value="300">Level 300</option>
              <option value="400">Level 400</option>
            </select>
          </div>
        </div>

        {/* Calendar grid */}
        <div className="overflow-x-auto">
          <div className="min-w-[860px]">

            {/* Day headers */}
            <div className="grid grid-cols-6 gap-2 mb-2">
              <div />
              {DAYS.map(day => (
                <div
                  key={day}
                  className="text-center text-xs font-semibold text-ucc-blue uppercase tracking-wider py-2 bg-white border border-ucc-border rounded-lg"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Morning + Afternoon rows */}
            {LABELS.map(label => (
              <div key={label} className="grid grid-cols-6 gap-2 mb-2">

                {/* Row label */}
                <div className="flex flex-col items-center justify-center bg-ucc-blue rounded-lg py-4 px-2">
                  <span className="text-white text-xs font-semibold">{label}</span>
                  <span className="text-blue-200 text-xs mt-1">
                    {label === "Morning" ? "08:00 – 11:00" : "13:00 – 16:00"}
                  </span>
                </div>

                {/* Day cells */}
                {DAYS.map(day => {
                  const courses = getCell(day, label)
                  return (
                    <div
                      key={day}
                      className="bg-white border border-ucc-border rounded-lg p-2 min-h-[110px] space-y-1.5"
                    >
                      {courses.length === 0 ? (
                        <p className="text-ucc-border text-xs text-center pt-8">—</p>
                      ) : (
                        courses.map(c => (
                          <div
                            key={c.course_code}
                            className={`border rounded-lg p-1.5 ${deptCard(c.department)}`}
                          >
                            <div className="flex items-center gap-1 mb-0.5 flex-wrap">
                              <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${deptBadge(c.department)}`}>
                                {c.department}
                              </span>
                              <span className={`text-xs font-bold ${deptText(c.department)}`}>
                                {c.course_code}
                              </span>
                            </div>
                            <p className={`text-xs leading-tight mb-0.5 ${deptText(c.department)}`}>
                              {c.course_name}
                            </p>
                            <p className="text-xs opacity-60">
                              L{c.level} &bull; {c.rooms_assigned.join(", ")}
                            </p>
                            <p className="text-xs opacity-50 truncate">{c.lecturer}</p>
                          </div>
                        ))
                      )}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 flex gap-6 items-center print:mt-2">
          <span className="text-xs text-ucc-muted font-medium">Legend:</span>
          <span className="flex items-center gap-1.5 text-xs text-blue-800">
            <span className="w-3 h-3 rounded bg-blue-100 border border-blue-200 inline-block" />
            Computer Science
          </span>
          <span className="flex items-center gap-1.5 text-xs text-red-800">
            <span className="w-3 h-3 rounded bg-red-100 border border-red-200 inline-block" />
            Information Technology
          </span>
        </div>

        {/* Conflicts panel */}
        {data?.unscheduled?.length > 0 && (
          <div className="mt-6 bg-white border border-red-200 rounded-xl p-5">
            <h2 className="text-ucc-red font-semibold text-sm mb-3">
              Conflict Log — {data.unscheduled.length} Unscheduled Course(s)
            </h2>
            <div className="space-y-2">
              {data.unscheduled.map(u => (
                <div
                  key={u.course_code}
                  className="flex items-start gap-3 bg-red-50 border border-red-100 rounded-lg px-4 py-2.5"
                >
                  <span className="text-red-600 font-semibold text-xs mt-0.5 shrink-0">
                    {u.course_code}
                  </span>
                  <div>
                    <p className="text-red-800 text-xs font-medium">{u.course_name}</p>
                    <p className="text-red-500 text-xs">{u.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Print footer */}
        <div className="hidden print:block mt-6 pt-4 border-t border-gray-300 text-center text-xs text-gray-500">
          Generated by UCC MIS Exam Timetable System &mdash; University of Cape Coast &copy; {new Date().getFullYear()}
        </div>

      </div>
    </div>
  )
}