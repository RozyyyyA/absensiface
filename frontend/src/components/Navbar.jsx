import { Link } from "react-router-dom"

export default function Navbar() {
  return (
    <nav className="w-full bg-blue-600 p-4 flex justify-between items-center text-white">
      <h1 className="text-xl font-bold">Attendance System</h1>
      <div className="space-x-4">
        <Link to="/" className="hover:underline">Absensi</Link>
        <Link to="/upload" className="hover:underline">Upload Dataset</Link>
      </div>
    </nav>
  )
}
