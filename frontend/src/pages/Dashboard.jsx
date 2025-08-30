import { useEffect, useState } from "react";
import { getCourses, getSessions } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [courses, setCourses] = useState([]);
  const [sessions, setSessions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const c = await getCourses();
        setCourses(c.data || []);
      } catch (e) { setCourses([]); }
      try {
        const s = await getSessions();
        setSessions((s.data || s).slice ? s.data || [] : []);
      } catch (e) { setSessions([]); }
    })();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>

      <section className="grid md:grid-cols-2 gap-6">
        {/* Matakuliah */}
        <div className="bg-white rounded-2xl shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold text-xl">Matakuliah</h2>
            <button
              onClick={() => navigate("/courses")}
              className="text-indigo-600 text-sm hover:underline"
            >
              Lihat semua
            </button>
          </div>
          <ul className="divide-y">
            {courses.length ? courses.slice(0,5).map(c => (
              <li key={c.id} className="py-3 flex flex-col md:flex-row justify-between items-start md:items-center hover:bg-gray-50 px-2 rounded transition-colors">
                <div>
                  <div className="font-medium text-gray-800">{c.name ?? c.title ?? c.nama}</div>
                  <div className="text-sm text-gray-500">Kode: {c.code ?? c.kode ?? "-"}</div>
                </div>
                <span className="mt-2 md:mt-0 inline-block bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full text-xs">
                  {c.students_count ?? "5"} Mahasiswa
                </span>
              </li>
            )) : (
              <li className="py-4 text-gray-500 text-center">Belum ada matakuliah</li>
            )}
          </ul>
        </div>

        {/* Sesi Terbaru */}
        <div className="bg-white rounded-2xl shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold text-xl">Sesi Terbaru</h2>
            <button
              onClick={() => navigate("/start-session")}
              className="text-indigo-600 text-sm hover:underline"
            >
              Mulai Sesi
            </button>
          </div>
          <ul className="divide-y">
            {sessions.length ? sessions.slice(0,6).map(s => (
              <li
                key={s.id}
                className="py-3 flex flex-col md:flex-row justify-between items-start md:items-center hover:bg-gray-50 px-2 rounded transition-colors"
              >
                <div>
                  <div className="font-medium text-gray-800">Sesi #{s.id} — Pertemuan {s.meeting_no ?? s.meeting}</div>
                  <div className="text-sm text-gray-500">Course: {s.course_id}</div>
                </div>
                <button
                  onClick={() => navigate(`/report/${s.id}`)}
                  className="mt-2 md:mt-0 px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 transition-colors"
                >
                  Report
                </button>
              </li>
            )) : (
              <li className="py-4 text-gray-500 text-center">Belum ada sesi</li>
            )}
          </ul>
        </div>
      </section>
    </div>
  );
}
