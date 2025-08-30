import { useEffect, useState } from "react";
import { getSessions, createSession } from "../services/api";

export default function SessionPage() {
  const [sessions, setSessions] = useState([]);
  const [form, setForm] = useState({ course_id: "", meeting_no: "" });

  const load = async () => {
    try {
      const r = await getSessions();
      setSessions(r.data || []);
    } catch (e) {
      setSessions([]);
    }
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await createSession({ course_id: form.course_id, meeting_no: Number(form.meeting_no) });
      setForm({ course_id: "", meeting_no: "" });
      load();
    } catch (e) {
      alert("Gagal membuat sesi");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Kelola Sesi</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Form Buat Sesi */}
        <form onSubmit={submit} className="bg-white p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-200">
          <div className="mb-4 text-lg font-medium">Buat Sesi Manual</div>
          <input
            placeholder="Course ID"
            value={form.course_id}
            onChange={e => setForm({ ...form, course_id: e.target.value })}
            className="w-full border px-3 py-2 rounded mb-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            placeholder="Pertemuan ke-"
            type="number"
            value={form.meeting_no}
            onChange={e => setForm({ ...form, meeting_no: e.target.value })}
            className="w-full border px-3 py-2 rounded mb-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            Buat Sesi
          </button>
        </form>

        {/* Daftar Sesi */}
        <div className="bg-white p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-200 overflow-auto">
          <div className="font-semibold text-lg mb-4">Daftar Sesi</div>
          <table className="w-full text-sm border-collapse">
            <thead className="bg-gray-50">
              <tr>
                <th className="p-2 text-left">ID</th>
                <th className="p-2 text-left">Course</th>
                <th className="p-2 text-center">Pertemuan</th>
              </tr>
            </thead>
            <tbody>
              {sessions.length ? sessions.map(s => (
                <tr key={s.id} className="border-t hover:bg-gray-50 transition-colors">
                  <td className="p-2">{s.id}</td>
                  <td className="p-2">{s.course_id}</td>
                  <td className="p-2 text-center">{s.meeting_no}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="3" className="p-4 text-gray-500 text-center">Belum ada sesi</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
