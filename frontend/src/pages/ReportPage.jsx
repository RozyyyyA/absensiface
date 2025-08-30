import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getReportBySession, markManual, downloadReportPdf } from "../services/api";

const STATUS = ["hadir", "sakit", "izin", "tanpa_keterangan", "alpha"];

export default function ReportPage() {
  const { sessionId } = useParams();
  const [report, setReport] = useState(null);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const fetchReport = async () => {
    try {
      const res = await getReportBySession(sessionId);
      setReport(res.data);
    } catch (error) {
      console.error(error);
      setReport(null);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [sessionId]);

  const onChange = async (student_id, status) => {
    if (!report) return;
    setSaving(student_id);
    try {
      await markManual({
        student_id,
        course_id: report.summary.course_id,
        meeting_no: report.summary.meeting_no,
        status,
      });
      await fetchReport();
    } catch (error) {
      console.error(error);
      alert("Gagal update status");
    } finally {
      setSaving(false);
    }
  };

  const onDownload = async () => {
    setDownloading(true);
    try {
      const blob = await downloadReportPdf(sessionId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_session_${sessionId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert("Gagal download PDF");
    } finally {
      setDownloading(false);
    }
  };

  if (!report) {
    return <div className="min-h-screen grid place-items-center">Memuat report...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-semibold">Report Sesi #{sessionId}</h1>
          <div className="text-sm text-gray-600">
            Course: {report.summary?.course_id ?? "-"} • Pertemuan {report.summary?.meeting_no ?? "-"}
          </div>
        </div>
        <div>
          <button
            className="px-3 py-2 bg-emerald-600 text-white rounded disabled:opacity-50"
            onClick={onDownload}
            disabled={downloading}
          >
            {downloading ? "Menyiapkan..." : "Unduh PDF"}
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-4 gap-3 mb-4">
        <Stat label="Total" value={report.summary?.total_students} />
        <Stat label="Hadir" value={report.summary?.hadir_count} />
        <Stat label="Sakit" value={report.summary?.sakit_count} />
        <Stat label="Tanpa Ket." value={report.summary?.tanpa_keterangan_count} />
      </div>

      <div className="bg-white rounded-2xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-3 text-left">Nama</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {report.absents?.length > 0 ? (
              report.absents.map((r) => (
                <tr key={r.student_id} className="border-t">
                  <td className="px-4 py-3">{r.name ?? r.student_name ?? "-"}</td>
                  <td className="px-4 py-3">{r.status ?? "-"}</td>
                  <td className="px-4 py-3 text-right">
                    <select
                      value={r.status}
                      onChange={(e) => onChange(r.student_id, e.target.value)}
                      disabled={saving === r.student_id}
                      className="px-2 py-1 border rounded"
                    >
                      {STATUS.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                  Tidak ada data.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-bold">{value ?? "-"}</div>
    </div>
  );
}
