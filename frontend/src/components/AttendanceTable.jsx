import { useEffect, useState } from "react"
import axios from "axios"

export default function AttendanceTable() {
  const [attendance, setAttendance] = useState([])

  useEffect(() => {
    axios.get("http://localhost:8000/attendance") // backend FastAPI/Flask endpoint
      .then(res => setAttendance(res.data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Daftar Absensi</h2>
      <table className="w-full border border-gray-300">
        <thead className="bg-gray-200">
          <tr>
            <th className="p-2 border">Nama</th>
            <th className="p-2 border">Tanggal</th>
            <th className="p-2 border">Status</th>
          </tr>
        </thead>
        <tbody>
          {attendance.map((a, i) => (
            <tr key={i} className="text-center">
              <td className="p-2 border">{a.name}</td>
              <td className="p-2 border">{new Date(a.date).toLocaleDateString()}</td>
              <td className="p-2 border">{a.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
