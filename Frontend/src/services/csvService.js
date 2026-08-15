import api from "./api";

export const csvService = {
  import: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/csv/import", form);
  },
  export: async () => {
    const response = await api.get("/csv/export", { responseType: "blob" });
    const url = window.URL.createObjectURL(response);
    const link = document.createElement("a");
    link.href = url;
    link.download = "expenses.csv";
    link.click();
    window.URL.revokeObjectURL(url);
  },
};
