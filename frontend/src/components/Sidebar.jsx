import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, BookOpen, History, Users, Calendar, Upload, LogOut } from "lucide-react";

export default function Sidebar() {
  const nav = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    nav("/login");
  };

  const LinkItem = ({ to, icon: Icon, children }) => (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition ${
          isActive
            ? "bg-indigo-600 text-white"
            : "text-gray-700 hover:bg-gray-100"
        }`
      }
    >
      <Icon className="w-5 h-5" />
      {children}
    </NavLink>
  );

  return (
    <aside className="h-screen w-64 bg-white border-r flex flex-col">
      <div className="px-6 py-4 text-lg font-bold text-indigo-700 border-b">
        Absensi FaceRec
      </div>
      <nav className="flex-1 p-4 flex flex-col gap-2">
        <LinkItem to="/dashboard" icon={LayoutDashboard}>Dashboard</LinkItem>
        <LinkItem to="/courses" icon={BookOpen}>Matakuliah</LinkItem>
        <LinkItem to="/sessions" icon={Calendar}>Sesi</LinkItem>
        <LinkItem to="/students" icon={Users}>Mahasiswa</LinkItem>
        <LinkItem to="/history" icon={History}>Riwayat</LinkItem>
        <LinkItem to="/upload" icon={Upload}>Upload</LinkItem>
      </nav>
      <div className="p-4 border-t">
        <button
          onClick={logout}
          className="flex items-center gap-2 px-4 py-2 w-full rounded-lg bg-rose-500 text-white text-sm hover:bg-rose-600"
        >
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </div>
    </aside>
  );
}
