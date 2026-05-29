import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const loginAdmin        = (credentials) => api.post("/auth/login", credentials)
export const uploadCSVs        = (formData)     => api.post("/upload/", formData)
export const generateTimetable = ()             => api.post("/timetable/generate")
export const getTimetable      = ()             => api.get("/timetable/")

export default api