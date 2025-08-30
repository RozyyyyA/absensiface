import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/api";
import loginIllustration from "../components/animasi/loginpage.jpg";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const { data } = await loginUser(email, password);

      // Simpan data login ke localStorage
      localStorage.setItem("token", data?.access_token || data?.token || "");
      localStorage.setItem("nama", data?.name || "");   // 🔥 simpan nama dosen
      localStorage.setItem("email", data?.email || "");

      navigate("/dashboard");
    } catch (err) {
      setError(err?.detail || "Login gagal");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="flex w-full max-w-4xl bg-white shadow-xl rounded-2xl overflow-hidden">
        
        {/* Bagian Kiri */}
        <div className="w-1/2 bg-indigo-600 flex flex-col justify-center items-center text-white p-10">
          <h2 className="text-3xl font-bold mb-4 text-center">
            Selamat Datang di <br /> FaceAbsensi
          </h2>
          <p className="text-center text-sm leading-relaxed mb-6">
            Sistem absensi modern berbasis Face Recognition
            untuk mendukung proses kehadiran yang lebih cepat,
            aman, dan efisien.
          </p>
          <img
            src={loginIllustration}
            alt="illustration"
            className="w-56"
          />
        </div>

        {/* Bagian Kanan (Form Login) */}
        <div className="w-1/2 p-8 flex flex-col justify-center">
          <h2 className="text-2xl font-bold text-center mb-6 text-gray-900">
            Login Dosen
          </h2>
          {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-700">Email</label>
              <input
                type="email"
                className="mt-1 w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="email@kampus.ac.id"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm text-gray-700">Password</label>
              <input
                type="password"
                className="mt-1 w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg transition"
            >
              Login
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-600">
            Belum punya akun? <span className="font-semibold">Hubungi Admin</span>
          </p>
        </div>
      </div>
    </div>
  );
}
