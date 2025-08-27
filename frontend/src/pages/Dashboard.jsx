import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard Dosen</h1>
      <div className="space-y-4">
        <button
          onClick={() => navigate("/attendance")}
          className="block bg-green-600 text-white px-4 py-2 rounded"
        >
          Mulai Absensi
        </button>
        <button
          onClick={() => navigate("/history")}
          className="block bg-blue-600 text-white px-4 py-2 rounded"
        >
          Riwayat Absensi
        </button>
        <button
          onClick={handleLogout}
          className="block bg-red-600 text-white px-4 py-2 rounded"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
