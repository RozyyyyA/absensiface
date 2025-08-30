import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getStudents, getEnrollments, enrollStudents, getCourseById } from "../services/api";

export default function EnrollPage() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [enrolled, setEnrolled] = useState([]);
  const [selected, setSelected] = useState([]);
  const [message, setMessage] = useState("");

  // Ambil data course, semua mahasiswa & yang sudah terdaftar
  useEffect(() => {
    const fetchData = async () => {
      try {
        // ambil course
        const resCourse = await getCourseById(courseId);
        setCourse(resCourse.data);

        // ambil mahasiswa
        const resStudents = await getStudents();
        const allStudents = resStudents.data || [];
        setStudents(allStudents);

        // ambil enrollment
        const resEnroll = await getEnrollments(courseId);
        const enrollmentData = resEnroll.data || [];

        // Join student_id dengan data mahasiswa
        const enrolledStudents = enrollmentData
          .map((en) => allStudents.find((s) => s.id === en.student_id))
          .filter(Boolean);

        setEnrolled(enrolledStudents);
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, [courseId]);

  const toggleSelect = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((sid) => sid !== id) : [...prev, id]
    );
  };

  const handleEnroll = async () => {
    try {
      await enrollStudents(courseId, selected);
      setMessage("Mahasiswa berhasil ditambahkan!");
      setSelected([]);

      // refresh daftar enrolled
      const resEnroll = await getEnrollments(courseId);
      const enrollmentData = resEnroll.data || [];
      const enrolledStudents = enrollmentData
        .map((en) => students.find((s) => s.id === en.student_id))
        .filter(Boolean);

      setEnrolled(enrolledStudents);
    } catch (err) {
      console.error(err);
      setMessage("Gagal menambahkan mahasiswa");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Enroll Mahasiswa</h1>
      <p className="text-gray-500 mb-2">
        Mata Kuliah: {course ? course.name : "Loading..."}
      </p>

      {/* Daftar semua mahasiswa */}
      <h2 className="text-lg font-semibold mt-4 mb-2">Daftar Mahasiswa</h2>
      <div className="border rounded-lg p-4 max-h-64 overflow-y-auto">
        {students.map((s) => {
          const isEnrolled = enrolled.some((e) => e.id === s.id);
          return (
            <div
              key={s.id}
              className="flex items-center justify-between border-b py-2"
            >
              <div>
                <p className="font-medium">{s.name}</p>
                <p className="text-sm text-gray-500">NIM: {s.nim}</p>
              </div>

              {isEnrolled ? (
                <span className="text-green-600 text-sm font-medium">
                  ✅ Sudah Terdaftar
                </span>
              ) : (
                <input
                  type="checkbox"
                  checked={selected.includes(s.id)}
                  onChange={() => toggleSelect(s.id)}
                />
              )}
            </div>
          );
        })}
      </div>

      <button
        onClick={handleEnroll}
        className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg"
        disabled={!selected.length}
      >
        Enroll yang Dipilih
      </button>

      {message && <p className="mt-3 text-green-600">{message}</p>}

      {/* Daftar mahasiswa yang sudah terdaftar */}
      <h2 className="text-lg font-semibold mt-6 mb-2">Sudah Terdaftar</h2>
      <div className="border rounded-lg p-4">
        {enrolled.length ? (
          enrolled.map((e) => (
            <div key={e.id} className="border-b py-2">
              <p className="font-medium">{e.name}</p>
              <p className="text-sm text-gray-500">NIM: {e.nim}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-500">Belum ada mahasiswa terdaftar</p>
        )}
      </div>
    </div>
  );
}
