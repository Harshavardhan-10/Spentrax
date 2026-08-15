import api from "./api";

export const expenseService = {
  list: (params) => api.get("/expenses", { params }),
  get: (id) => api.get(`/expenses/${id}`),
  create: (payload) => api.post("/expenses", payload),
  update: (id, payload) => api.put(`/expenses/${id}`, payload),
  remove: (id) => api.delete(`/expenses/${id}`),
};
