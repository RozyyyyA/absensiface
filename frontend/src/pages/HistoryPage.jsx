import { useState } from "react";
import ReportPage from "./ReportPage";

export default function HistoryPage() {
  const [selected, setSelected] = useState(null);
  const meetings = [1, 2, 3]; // contoh dummy

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Riwayat Absensi</h2>
      <div className="space-x-2 mb-6">
        {meetings.map((m) => (
          <button
            key={m}
            onClick={() => setSelected(m)}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Pertemuan {m}
          </button>
        ))}
      </div>
      {selected && <ReportPage />}
    </div>
  );
}
