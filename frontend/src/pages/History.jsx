import { useEffect, useState } from "react";
import { getSessions } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function History() {
  const [sessions, setSessions] = useState([]);
  const nav = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const s = await getSessions();
        setSessions(s.data || []);
      } catch (e) {
        setSessions([]);
      }
    })();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Riwayat Sesi</h1>

      <div className="bg-white rounded-2xl shadow-md overflow-x-auto">
        <table className="w-full text-sm table-auto border-collapse">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left">Session ID</th>
              <th className="px-4 py-3 text-left">Course ID</th>
              <th className="px-4 py-3 text-left">Pertemuan</th>
              <th className="px-4 py-3 text-left">Mulai</th>
              <th className="px-4 py-3 text-left">Selesai</th>
              <th className="px-4 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {sessions.length ? sessions.map(s => (
              <tr key={s.id} className="border-t hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3">{s.id}</td>
                <td className="px-4 py-3">{s.course_id}</td>
                <td className="px-4 py-3">{s.meeting_no}</td>
                <td className="px-4 py-3">{s.started_at ?? "-"}</td>
                <td className="px-4 py-3">{s.finished_at ?? "-"}</td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => nav(`/report/${s.id}`)}
                    className="px-3 py-1.5 rounded-md bg-indigo-600 text-white text-sm hover:bg-indigo-700 transition-colors"
                  >
                    Lihat
                  </button>
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan="6" className="px-4 py-10 text-center text-gray-500">
                  Belum ada sesi
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
