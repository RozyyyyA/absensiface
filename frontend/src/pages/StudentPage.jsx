import { useEffect, useState } from "react";
import { getStudents, createStudent, deleteStudent } from "../services/api";

export default function StudentPage() {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState({ name: "", nim: "" });

  const load = async () => {
    try {
      const r = await getStudents();
      setRows(r.data || []);
    } catch (e) {
      setRows([]);
    }
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await createStudent(form);
      setForm({ name: "", nim: "" });
      load();
    } catch (e) {
      alert("Gagal simpan");
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Hapus mahasiswa ini?")) return;
    try {
      await deleteStudent(id);
      load();
    } catch (e) {
      alert("Gagal hapus");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Kelola Mahasiswa</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Form Tambah Mahasiswa */}
        <form onSubmit={submit} className="bg-white p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-200">
          <div className="font-semibold mb-4 text-lg">Tambah Mahasiswa</div>
          <input
            placeholder="Nama"
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            className="w-full border px-3 py-2 rounded mb-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            placeholder="NIM"
            value={form.nim}
            onChange={e => setForm({ ...form, nim: e.target.value })}
            className="w-full border px-3 py-2 rounded mb-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            Simpan
          </button>
        </form>

        {/* Tabel Daftar Mahasiswa */}
        <div className="bg-white p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-200 overflow-auto">
          <div className="font-semibold text-lg mb-4">Daftar Mahasiswa</div>
          <table className="w-full text-sm border-collapse">
            <thead className="bg-gray-50">
              <tr>
                <th className="p-2 text-left">Nama</th>
                <th className="p-2 text-left">NIM</th>
                <th className="p-2 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody>
              {rows.length ? rows.map(r => (
                <tr key={r.id} className="border-t hover:bg-gray-50 transition-colors">
                  <td className="p-2">{r.name ?? r.nama}</td>
                  <td className="p-2">{r.nim}</td>
                  <td className="p-2 text-right">
                    <button
                      onClick={() => handleDelete(r.id)}
                      className="px-3 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200 transition-colors"
                    >
                      Hapus
                    </button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="3" className="p-4 text-gray-500 text-center">
                    Belum ada mahasiswa
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
