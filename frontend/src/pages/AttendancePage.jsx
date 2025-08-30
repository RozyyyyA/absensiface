import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import { getSessions, postAttendance } from "../services/api";

export default function AttendancePage() {
  const webcamRef = useRef(null);
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const { data } = await getSessions();
        setSessions(data || []);
        if (data?.length) setSessionId(String(data[0].id ?? data[0]._id ?? data[0].session_id));
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  const captureAndSend = async () => {
    if (!webcamRef.current) return;
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;
    // convert base64 to Blob
    const res = await fetch(imageSrc);
    const blob = await res.blob();
    const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
    try {
      setStatus("Mengirim...");
      await postAttendance(file, sessionId);
      setStatus("✅ Absensi berhasil dikirim");
    } catch (e) {
      setStatus("❌ Gagal mengirim absensi");
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setStatus("Mengirim...");
      await postAttendance(file, sessionId);
      setStatus("✅ Absensi berhasil dikirim");
    } catch (e) {
      setStatus("❌ Gagal mengirim absensi");
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="space-y-4">
        <label className="block text-sm text-gray-700">Pilih Sesi</label>
        <select
          value={sessionId}
          onChange={(e) => setSessionId(e.target.value)}
          className="w-full border rounded-lg px-3 py-2"
        >
          {sessions.map((s) => (
            <option key={s.id ?? s.session_id} value={s.id ?? s.session_id}>
              {s.title ?? s.nama ?? `Sesi ${s.id}`}
            </option>
          ))}
        </select>

        <div className="rounded-lg overflow-hidden border bg-black/5 aspect-video">
          <Webcam ref={webcamRef} screenshotFormat="image/jpeg" className="w-full h-full object-cover" />
        </div>

        <div className="flex gap-2">
          <button onClick={captureAndSend} className="px-4 py-2 bg-indigo-600 text-white rounded-lg">
            Capture & Kirim
          </button>
          <label className="px-4 py-2 bg-gray-100 rounded-lg cursor-pointer">
            Upload Foto
            <input type="file" accept="image/*" className="hidden" onChange={handleUpload} />
          </label>
        </div>

        {status && <p className="text-sm text-gray-700">{status}</p>}
      </div>

      <div className="p-4 border rounded-lg bg-white">
        <h3 className="font-semibold mb-2">Tips</h3>
        <ul className="list-disc ml-5 text-sm text-gray-600 space-y-1">
          <li>Pencahayaan cukup dan wajah menghadap kamera.</li>
          <li>Jika gagal, coba ulangi capture atau upload dari galeri.</li>
        </ul>
      </div>
    </div>
  );
}
