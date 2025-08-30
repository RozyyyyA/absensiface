import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { createSession } from "../services/api";

export default function StartSession() {
  const { state } = useLocation();
  const course = state?.course;
  const [meeting, setMeeting] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    if (!course?.id) return alert("Pilih matakuliah dulu.");
    setLoading(true);
    try {
      const res = await createSession({ course_id: course.id, meeting_no: Number(meeting) });
      const session = res.data;
      // navigate to scan with state
      navigate("/scan", { state: { course_id: course.id, meeting_no: session.meeting_no ?? meeting, session_id: session.id } });
    } catch (err) {
      alert("Gagal membuat session");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Mulai Sesi Absensi</h1>
      <div className="bg-white p-6 rounded-2xl shadow max-w-xl">
        <div className="mb-4">
          <div className="font-medium">Matakuliah</div>
          <div className="text-gray-700">{course ? (course.name ?? course.title) : "Belum memilih"}</div>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-600">Pertemuan ke-</label>
            <input type="number" min={1} value={meeting} onChange={(e) => setMeeting(e.target.value)} className="w-full border rounded px-3 py-2" required />
          </div>
          <div className="flex gap-3">
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded" disabled={loading}>
              {loading ? "Memulai..." : "Mulai Sesi"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
