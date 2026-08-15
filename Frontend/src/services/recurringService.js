import api from "./api";

export const recurringService = {
  list: () => api.get("/recurring"),
  detect: () => api.post("/recurring/detect"),
  toggle: (id, isActive) => api.patch(`/recurring/${id}`, { is_active: isActive }),
  remove: (id) => api.delete(`/recurring/${id}`),
};
