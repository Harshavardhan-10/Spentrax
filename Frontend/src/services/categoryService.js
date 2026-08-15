import api from "./api";

export const categoryService = {
  list: () => api.get("/categories"),
  create: (payload) => api.post("/categories", payload),
  update: (id, payload) => api.put(`/categories/${id}`, payload),
  remove: (id) => api.delete(`/categories/${id}`),
};
