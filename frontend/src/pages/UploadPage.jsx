import { useState } from "react"
import axios from "axios"

export default function UploadPage() {
  const [file, setFile] = useState(null)

  const handleUpload = async () => {
    if (!file) return alert("Pilih file terlebih dahulu")
    const formData = new FormData()
    formData.append("file", file)

    try {
      await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      alert("Upload berhasil")
    } catch (err) {
      console.error(err)
      alert("Upload gagal")
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-lg font-semibold mb-4">Upload Dataset Wajah</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} className="mb-4" />
      <button 
        onClick={handleUpload} 
        className="bg-blue-600 text-white px-4 py-2 rounded">
        Upload
      </button>
    </div>
  )
}
