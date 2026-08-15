export const PAYMENT_METHODS = [
  "CASH",
  "CREDIT_CARD",
  "DEBIT_CARD",
  "UPI",
  "BANK_TRANSFER",
  "OTHER",
];

export const FREQUENCIES = ["WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"];

export const BUDGET_STATUS = {
  HEALTHY: { label: "Healthy", color: "#22c55e" },
  WARNING: { label: "Warning", color: "#f59e0b" },
  CRITICAL: { label: "Critical", color: "#f97316" },
  EXCEEDED: { label: "Exceeded", color: "#ef4444" },
};

export const SEVERITY = {
  INFO: { label: "Info", color: "#3b82f6" },
  WARNING: { label: "Warning", color: "#f59e0b" },
  IMPORTANT: { label: "Important", color: "#ef4444" },
};

export const CHART_COLORS = [
  "#6366f1",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
  "#a855f7",
  "#ec4899",
  "#84cc16",
  "#f97316",
  "#14b8a6",
  "#8b5cf6",
  "#64748b",
];

export function getMonthName(month) {
  return new Date(2000, month - 1, 1).toLocaleString("en-IN", { month: "long" });
}
