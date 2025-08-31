import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000", // sesuaikan dengan backend FastAPI-mu
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// -------- AUTH --------
export const loginUser = (email, password) =>
  API.post("/auth/login", { email, password });

// ---- COURSES ----
export const getCourses = () => API.get("/courses/");

export const getCourseById = (id) => API.get(`/courses/${id}`);

//--- ENROLLMENT ---
export const getEnrollments = (courseId) =>
  API.get(`/enrollments/${courseId}`);

export const enrollStudents = async (courseId, studentIds) => {
  const res = await fetch("http://localhost:8000/enrollments/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`
    },
    body: JSON.stringify({
      course_id: Number(courseId),        // ubah ke int
      student_ids: studentIds.map(Number) // pastikan array of int
    })
  });
  if (!res.ok) throw new Error("Failed to enroll");
  return res.json();
};

// -------- STUDENT --------
export const getStudents = () => API.get("/student/");
export const createStudent = (data) => API.post("/student/", data);
export const updateStudent = (id, data) => API.put(`/student/${id}`, data);
export const deleteStudent = (id) => API.delete(`/student/${id}`);

// -------- SESSION --------
export const getSessions = () => API.get("/session/");
export const createSession = (payload) => API.post("/session/", payload); // {course_id, meeting_no}
export const finishSession = (sessionId) => API.post(`/session/${sessionId}/finish`);


// -------- ATTENDANCE --------
export const markFace = ({ file, course_id, meeting_no }) => {
  const form = new FormData();
  form.append("file", file);
  // course_id & meeting_no sebagai query params (sesuai FastAPI-mu)
  return API.post(`/attendance/mark/face?course_id=${course_id}&meeting_no=${meeting_no}`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const markManual = ({ student_id, course_id, meeting_no, status }) =>
  API.post("/attendance/mark/manual", { student_id, course_id, meeting_no, status });

// get attendance list per session (if implemented)
export const getAttendance = (session_id) =>
  API.get("/attendance/", { params: { session_id } });

// update attendance by id (if implemented)
export const updateAttendance = (attendance_id, payload) =>
  API.put(`/attendance/${attendance_id}`, payload);

// -------- REPORT --------
export const getReportBySession = (sessionId) => API.get(`/report/${sessionId}`);
export const downloadReportPdf = async (sessionId) => {
  const res = await API.get(`/report/${sessionId}/pdf`, {
    responseType: "blob", // wajib supaya hasilnya blob
  });
  return res.data; // <-- balikin blob
};

export default API;
