import axios from "axios";

export class ApiError extends Error {
  constructor(message, code = null, status = null) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => {
    const body = response.data;
    if (body && typeof body === "object" && "success" in body) {
      if (body.success) {
        return body.data;
      }
      throw new ApiError(body.message || "Request failed.", body.error_code, response.status);
    }
    return body;
  },
  (error) => {
    const status = error.response?.status;
    const data = error.response?.data;
    if (status === 401 && !window.location.pathname.startsWith("/login")) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    const message = data?.message || error.message || "Network error. Please try again.";
    throw new ApiError(message, data?.error_code, status);
  }
);

export default api;
