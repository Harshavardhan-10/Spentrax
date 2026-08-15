import api from "./api";

export const aiService = {
  categorize: (payload) => api.post("/ai/categorize", payload),
  insights: (params) => api.get("/ai/insights", { params }),
  summary: (params) => api.get("/ai/summary", { params }),
  recommendations: () => api.get("/ai/recommendations"),
  anomalies: () => api.get("/ai/anomalies"),
};
