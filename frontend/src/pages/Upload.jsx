import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { uploadCSVs, generateTimetable } from "../services/api"
import uccLogo from "../assets/ucc_logo.png"

export default function Upload() {
  const navigate = useNavigate()
  const adminName = localStorage.getItem("admin_name") || "Admin"

  const [files, setFiles] = useState({
    courses_file:  null,
    rooms_file:    null,
    slots_file:    null,
  })
  const [status,  setStatus]  = useState(null)   // { type: "success"|"error", message }
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [uploadDone, setUploadDone] = useState(false)

  const handleFile = (e) => {
    setFiles({ ...files, [e.target.name]: e.target.files[0] })
    setStatus(null)
  }

  const handleUpload = async (e) => {
    e.preventDefault()

    if (!files.courses_file || !files.rooms_file || !files.slots_file) {
      setStatus({ type: "error", message: "Please select all three CSV files before uploading." })
      return
    }

    setLoading(true)
    setStatus(null)

    try {
      const formData = new FormData()
      formData.append("courses_file", files.courses_file)
      formData.append("rooms_file",   files.rooms_file)
      formData.append("slots_file",   files.slots_file)

      const res = await uploadCSVs(formData)
      const d   = res.data

      setStatus({
        type: "success",
        message: `Upload successful — ${d.courses_loaded} courses, ${d.rooms_loaded} rooms, ${d.slots_loaded} time slots loaded.`,
      })
      setUploadDone(true)
    } catch (err) {
      setStatus({
        type: "error",
        message: err.response?.data?.detail || "Upload failed. Please check your CSV files.",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    setStatus(null)
    try {
      await generateTimetable()
      navigate("/timetable")
    } catch (err) {
      setStatus({
        type: "error",
        message: err.response?.data?.detail || "Generation failed. Please try again.",
      })
    } finally {
      setGenerating(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("admin_name")
    navigate("/login")
  }

  return (
    <div className="min-h-screen bg-ucc-gray">

      {/* Top bar */}
      <div className="h-1 w-full bg-ucc-blue fixed top-0 left-0 z-50" />

      {/* Navbar */}
      <nav className="bg-white border-b border-ucc-border px-6 py-3 flex items-center justify-between">
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
          <span className="text-ucc-muted text-sm">Welcome, {adminName}</span>
          <button
            onClick={handleLogout}
            className="text-sm text-ucc-red hover:underline"
          >
            Logout
          </button>
        </div>
      </nav>

      {/* Page content */}
      <div className="max-w-2xl mx-auto px-4 py-12">

        {/* Page header */}
        <div className="mb-8">
          <h1 className="text-ucc-blue text-2xl font-semibold">Upload Exam Data</h1>
          <p className="text-ucc-muted text-sm mt-1">
            Upload the three CSV files to generate the exam timetable.
            All files must follow the required column structure.
          </p>
          <div className="w-12 h-0.5 bg-ucc-red rounded-full mt-3" />
        </div>

        {/* Upload card */}
        <form onSubmit={handleUpload} className="bg-white border border-ucc-border rounded-xl p-6 space-y-6">

          {/* Courses */}
          <div>
            <label className="block text-sm font-medium text-ucc-text mb-1">
              Courses CSV
            </label>
            <p className="text-xs text-ucc-muted mb-2">
              Required columns: course_code, course_name, department, level, enrolled_count, lecturer
            </p>
            <input
              type="file"
              name="courses_file"
              accept=".csv"
              onChange={handleFile}
              className="w-full text-sm text-ucc-muted border border-ucc-border rounded-lg px-3 py-2 bg-ucc-gray file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-ucc-blue file:text-white hover:file:bg-ucc-blueDark"
            />
            {files.courses_file && (
              <p className="text-xs text-green-600 mt-1">✓ {files.courses_file.name}</p>
            )}
          </div>

          {/* Rooms */}
          <div>
            <label className="block text-sm font-medium text-ucc-text mb-1">
              Rooms CSV
            </label>
            <p className="text-xs text-ucc-muted mb-2">
              Required columns: room_id, room_name, building, capacity
            </p>
            <input
              type="file"
              name="rooms_file"
              accept=".csv"
              onChange={handleFile}
              className="w-full text-sm text-ucc-muted border border-ucc-border rounded-lg px-3 py-2 bg-ucc-gray file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-ucc-blue file:text-white hover:file:bg-ucc-blueDark"
            />
            {files.rooms_file && (
              <p className="text-xs text-green-600 mt-1">✓ {files.rooms_file.name}</p>
            )}
          </div>

          {/* Time Slots */}
          <div>
            <label className="block text-sm font-medium text-ucc-text mb-1">
              Time Slots CSV
            </label>
            <p className="text-xs text-ucc-muted mb-2">
              Required columns: slot_id, week, day, label, start_time, end_time
            </p>
            <input
              type="file"
              name="slots_file"
              accept=".csv"
              onChange={handleFile}
              className="w-full text-sm text-ucc-muted border border-ucc-border rounded-lg px-3 py-2 bg-ucc-gray file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-ucc-blue file:text-white hover:file:bg-ucc-blueDark"
            />
            {files.slots_file && (
              <p className="text-xs text-green-600 mt-1">✓ {files.slots_file.name}</p>
            )}
          </div>

          {/* Status message */}
          {status && (
            <div className={`text-sm rounded-lg px-4 py-3 ${
              status.type === "success"
                ? "bg-green-50 border border-green-200 text-green-700"
                : "bg-red-50 border border-red-200 text-red-700"
            }`}>
              {status.message}
            </div>
          )}

          {/* Upload button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-ucc-blue hover:bg-ucc-blueDark text-white font-medium text-sm py-3 rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Uploading..." : "Upload CSV Files"}
          </button>
        </form>

        {/* Generate button — only shows after successful upload */}
        {uploadDone && (
          <div className="mt-4 bg-white border border-ucc-border rounded-xl p-6">
            <p className="text-sm text-ucc-text font-medium mb-1">
              Data uploaded successfully
            </p>
            <p className="text-xs text-ucc-muted mb-4">
              Click below to run the scheduling algorithm and generate the exam timetable.
            </p>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full bg-ucc-red hover:bg-red-700 text-white font-medium text-sm py-3 rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {generating ? "Generating timetable..." : "Generate Exam Timetable"}
            </button>
          </div>
        )}

      </div>
    </div>
  )
}