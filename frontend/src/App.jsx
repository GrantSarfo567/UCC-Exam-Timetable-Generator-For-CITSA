import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login    from "./pages/Login"
import Upload   from "./pages/Upload"
import Timetable from "./pages/Timetable"

// Simple auth guard — checks for token in localStorage
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token")
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/upload" element={
          <PrivateRoute><Upload /></PrivateRoute>
        } />
        <Route path="/timetable" element={
          <PrivateRoute><Timetable /></PrivateRoute>
        } />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}