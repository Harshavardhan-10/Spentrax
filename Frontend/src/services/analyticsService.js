import api from "./api";

export const analyticsService = {
  monthly: (params) => api.get("/analytics/monthly", { params }),
  categories: (params) => api.get("/analytics/categories", { params }),
  trends: (params) => api.get("/analytics/trends", { params }),
  comparison: (params) => api.get("/analytics/comparison", { params }),
  dashboard: () => api.get("/dashboard"),
  async overview(params) {
    const [monthly, categories, trends, comparison] = await Promise.all([
      api.get("/analytics/monthly", { params }),
      api.get("/analytics/categories", { params }),
      api.get("/analytics/trends", { params: { months: 12 } }),
      api.get("/analytics/comparison", { params }),
    ]);
    return { monthly, categories, trends, comparison };
  },
};
