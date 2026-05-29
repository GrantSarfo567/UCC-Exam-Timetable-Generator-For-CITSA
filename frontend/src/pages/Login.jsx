import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { loginAdmin } from "../services/api"
import uccLogo from "../assets/ucc_logo.png"

export default function Login() {
  const navigate  = useNavigate()
  const [form, setForm]       = useState({ username: "", password: "" })
  const [error, setError]     = useState("")
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError("")
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.username || !form.password) {
      setError("Please enter both username and password.")
      return
    }
    setLoading(true)
    try {
      const res = await loginAdmin(form)
      localStorage.setItem("token",      res.data.access_token)
      localStorage.setItem("admin_name", res.data.admin_name)
      navigate("/upload")
    } catch (err) {
      setError(
        err.response?.data?.detail || "Login failed. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ucc-gray flex flex-col items-center justify-center px-4">

      {/* Top accent bar */}
      <div className="fixed top-0 left-0 w-full h-1 bg-ucc-blue z-50" />

      <div className="w-full max-w-md bg-white rounded-xl border border-ucc-border shadow-sm px-8 py-10">

        {/* Gradient line */}
        <div className="h-1 w-full rounded-full mb-8"
          style={{ background: "linear-gradient(90deg, #1A3A6B, #FFD700, #CC0000)" }}
        />

        {/* Header */}
        <div className="flex flex-col items-center mb-8">
          <img
            src={uccLogo}
            alt="University of Cape Coast Logo"
            className="w-20 h-20 object-contain mb-3"
          />
          <h1 className="text-ucc-blue font-semibold text-base text-center tracking-wide">
            University of Cape Coast
          </h1>
          <p className="text-ucc-muted text-xs mt-1 text-center">
            Management Information System
          </p>
          <div className="w-10 h-0.5 bg-ucc-red rounded-full my-3" />
          <p className="text-ucc-blue text-sm font-medium text-center">
            Exam Timetable Generator
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-ucc-text mb-1.5">
              Username
            </label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="Enter your username"
              className="w-full px-4 py-2.5 rounded-lg border border-ucc-border bg-ucc-gray text-ucc-text text-sm focus:outline-none focus:border-ucc-blue focus:bg-white transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-ucc-text mb-1.5">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className="w-full px-4 py-2.5 rounded-lg border border-ucc-border bg-ucc-gray text-ucc-text text-sm focus:outline-none focus:border-ucc-blue focus:bg-white transition-colors"
            />
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2.5">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-ucc-blue hover:bg-ucc-blueDark text-white font-medium text-sm py-3 rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed tracking-wide"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        {/* Footer */}
        <p className="text-center text-xs text-ucc-muted mt-8">
          University of Cape Coast &copy; {new Date().getFullYear()} &mdash; MIS Department
        </p>
      </div>
    </div>
  )
}