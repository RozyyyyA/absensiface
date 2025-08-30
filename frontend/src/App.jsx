// src/App.jsx
import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Sidebar from "./components/Sidebar";

// Pages
import Login from "./pages/Login";   // ✅ tambahkan ini
import Dashboard from "./pages/Dashboard";
import CourseSelect from "./pages/CourseSelect";
import EnrollPage from "./pages/EnrollPage";
import StartSession from "./pages/StartSession";
import ScanAttendance from "./pages/ScanAttendance";
import ReportPage from "./pages/ReportPage";
import History from "./pages/History";
import StudentPage from "./pages/StudentPage";
import SessionPage from "./pages/SessionPage";
import UploadPage from "./pages/UploadPage";

// Layout wrapper (semua halaman setelah login pakai Sidebar)
function Layout() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-6">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/courses" element={<CourseSelect />} />
          <Route path="/courses/:courseId/enroll" element={<EnrollPage />} />
          <Route path="/start-session" element={<StartSession />} />
          <Route path="/scan" element={<ScanAttendance />} />
          <Route path="/report/:sessionId" element={<ReportPage />} />
          <Route path="/history" element={<History />} />
          <Route path="/students" element={<StudentPage />} />
          <Route path="/sessions" element={<SessionPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      {/* PUBLIC */}
      <Route path="/login" element={<Login />} />   {/* ✅ ini route login */}

      {/* PROTECTED */}
      <Route element={<ProtectedRoute />}>
        <Route path="/*" element={<Layout />} />
      </Route>

      {/* fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
