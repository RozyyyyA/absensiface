import { useEffect, useState } from "react";
import { getCourses } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function CourseSelect() {
  const [courses, setCourses] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const res = await getCourses();
        setCourses(res.data || []);
      } catch (e) {
        setCourses([]);
      }
    })();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Pilih Mata Kuliah</h1>
      <div className="grid md:grid-cols-2 gap-6">
        {courses.length ? courses.map(c => (
          <div
            key={c.id}
            className="bg-white rounded-2xl shadow-md p-6 flex flex-col md:flex-row justify-between items-start md:items-center hover:shadow-lg transition-shadow duration-200"
          >
            <div>
              <div className="font-semibold text-gray-800 text-lg">{c.name ?? c.title}</div>
              <div className="text-sm text-gray-500 mt-1">Kode: {c.code ?? c.kode ?? "-"}</div>
            </div>
            <div className="mt-4 md:mt-0 flex gap-2">
              <button
                onClick={() => navigate("/start-session", { state: { course: c } })}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
              >
                Pilih
              </button>
              <button
                onClick={() => navigate(`/courses/${c.id}/enroll`)}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                Enroll Mahasiswa
              </button>
            </div>
          </div>
        )) : (
          <div className="col-span-2 text-gray-500 text-center py-10">Belum ada matakuliah</div>
        )}
      </div>
    </div>
  );
}
