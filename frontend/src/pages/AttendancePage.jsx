import { useState } from "react";
import Webcam from "react-webcam";
import api from "../services/api";

export default function AttendancePage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  const course_id = 1; // contoh fix, bisa dari props/URL
  const meeting_no = 1;

  const captureAndSend = async (webcamRef) => {
    if (!webcamRef.current) return;
    const imageSrc = webcamRef.current.getScreenshot();
    const blob = await fetch(imageSrc).then((res) => res.blob());
    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");

    try {
      setLoading(true);
      const res = await api.post(
        `/attendance/mark/face?course_id=${course_id}&meeting_no=${meeting_no}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setLogs((prev) => [
        ...prev,
        `✔️ Student ${res.data.student_id} hadir (conf: ${res.data.confidence})`,
      ]);
    } catch (err) {
      setLogs((prev) => [...prev, `❌ ${err.response?.data?.detail}`]);
    } finally {
      setLoading(false);
    }
  };

  const webcamRef = React.useRef(null);

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Absensi Wajah</h2>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        className="border rounded"
      />
      <div className="mt-4 space-x-2">
        <button
          onClick={() => captureAndSend(webcamRef)}
          className="bg-green-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          {loading ? "Memproses..." : "Ambil & Kirim Frame"}
        </button>
      </div>
      <div className="mt-6 bg-gray-100 p-4 rounded">
        <h3 className="font-bold">Log Absensi:</h3>
        <ul className="list-disc ml-6">
          {logs.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
