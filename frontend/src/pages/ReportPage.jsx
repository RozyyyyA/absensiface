import { useEffect, useState } from "react";
import api from "../services/api";

export default function ReportPage() {
  const [report, setReport] = useState(null);
  const course_id = 1;
  const meeting_no = 1;

  useEffect(() => {
    api
      .get(`/report/${course_id}/${meeting_no}`)
      .then((res) => setReport(res.data))
      .catch((err) => console.error(err));
  }, []);

  if (!report) return <p className="p-6">Loading report...</p>;

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Laporan Absensi</h2>
      <div className="mb-4">
        <p>Total Mahasiswa: {report.summary.total_students}</p>
        <p>Hadir: {report.summary.hadir_count}</p>
        <p>Sakit: {report.summary.sakit_count}</p>
        <p>Tanpa Keterangan: {report.summary.tanpa_keterangan_count}</p>
      </div>
      <h3 className="font-bold">Mahasiswa tidak hadir:</h3>
      <ul className="list-disc ml-6">
        {report.absents.map((st) => (
          <li key={st.student_id}>
            {st.name} ({st.nim}) - {st.status}
          </li>
        ))}
      </ul>
    </div>
  );
}
