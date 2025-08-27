// src/services/api.js
import axios from "axios";

const API_URL = "http://localhost:8000"; // ganti sesuai backend FastAPI kamu

const api = axios.create({
  baseURL: API_URL,
});

// Tambahkan Authorization header jika ada token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// fungsi login
export const loginUser = async (email, password) => {
  try {
    const res = await api.post("/auth/login", { email, password });
    return res.data;
  } catch (err) {
    throw err.response?.data || { detail: "Login gagal" };
  }
};


export default api;
