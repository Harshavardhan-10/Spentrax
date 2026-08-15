import api from "./api";

export const budgetService = {
  list: (params) => api.get("/budgets", { params }),
  create: (payload) => api.post("/budgets", payload),
  update: (id, payload) => api.put(`/budgets/${id}`, payload),
  remove: (id) => api.delete(`/budgets/${id}`),
};
