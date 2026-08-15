import api from "./api";

export const authService = {
  register: (payload) => api.post("/auth/register", payload),
  login: (payload) => api.post("/auth/login", payload),
  me: () => api.get("/auth/me"),
  logout: () => api.post("/auth/logout"),
  updateProfile: (payload) => api.put("/users/me", payload),
  changePassword: (payload) => api.post("/users/me/change-password", payload),
};
