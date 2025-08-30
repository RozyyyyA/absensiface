import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { markFace, finishSession } from "../services/api";

export default function ScanAttendance() {
  const { state } = useLocation();
  const { course_id, meeting_no, session_id } = state || {};
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [log, setLog] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const navigate = useNavigate();

  const push = (m) =>
    setLog((prev) => [{ id: Date.now(), m }, ...prev].slice(0, 50));

  useEffect(() => {
    // aktifkan kamera
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" },
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setStreaming(true);
        }
      } catch (err) {
        alert("Tidak bisa akses kamera: " + err.message);
      }
    };

    startCamera();
    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  useEffect(() => {
    if (!streaming) return;
    const interval = setInterval(async () => {
      if (!videoRef.current || !canvasRef.current) return;
      const ctx = canvasRef.current.getContext("2d");
      ctx.drawImage(videoRef.current, 0, 0, 320, 240);

      canvasRef.current.toBlob(async (blob) => {
        if (!blob) return;
        try {
          const file = new File([blob], "frame.jpg", { type: "image/jpeg" });
          const res = await markFace({ file, course_id, meeting_no });
          const d = res.data || {};
          push(
            `${d.status} - student_id:${d.student_id ?? "-"} conf:${
              d.confidence ?? 0
            }`
          );
        } catch (err) {
          push(`ERR: ${err?.response?.data?.detail ?? err.message}`);
        }
      }, "image/jpeg");
    }, 3000); // kirim frame tiap 3 detik

    return () => clearInterval(interval);
  }, [streaming]);

  const onClose = async () => {
    if (!session_id) return alert("No session");
    try {
      await finishSession(session_id);
      navigate(`/report/${session_id}`);
    } catch (e) {
      alert("Gagal menutup sesi");
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Scan Wajah Realtime</h1>
      <div className="bg-white p-6 rounded-2xl shadow max-w-2xl">
        <div className="mb-4 text-sm text-gray-600">
          Course: {course_id} — Pertemuan: {meeting_no} — Session: {session_id}
        </div>

        <div className="mb-4">
          <video ref={videoRef} autoPlay playsInline width="320" height="240" />
          <canvas ref={canvasRef} width="320" height="240" hidden />
        </div>

        <button
          onClick={onClose}
          className="px-3 py-2 bg-rose-500 text-white rounded"
        >
          Tutup Sesi & Lihat Report
        </button>

        <div className="mt-6 bg-gray-50 p-4 rounded">
          <h3 className="font-medium mb-2">Log</h3>
          <ul className="text-sm max-h-48 overflow-auto">
            {log.length ? (
              log.map((l) => (
                <li key={l.id} className="font-mono">
                  {l.m}
                </li>
              ))
            ) : (
              <li className="text-gray-500">Belum ada log</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
