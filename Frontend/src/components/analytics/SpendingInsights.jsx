import { formatCurrency } from "../../utils/formatCurrency";

export default function SpendingInsights({ analytics }) {
  if (!analytics) return null;

  const rows = [
    { label: "Total spent", value: formatCurrency(analytics.total_expenses) },
    { label: "Average daily", value: formatCurrency(analytics.avg_daily_spending) },
    { label: "Average monthly (3 mo)", value: formatCurrency(analytics.avg_monthly_spending) },
    { label: "Highest expense", value: formatCurrency(analytics.highest_expense?.amount) },
    { label: "Lowest expense", value: formatCurrency(analytics.lowest_expense?.amount) },
    {
      label: "Month-over-month",
      value:
        analytics.month_over_month_change === null || analytics.month_over_month_change === undefined
          ? "—"
          : `${analytics.month_over_month_change > 0 ? "+" : ""}${analytics.month_over_month_change}%`,
    },
  ];

  return (
    <div className="insight-stats">
      {rows.map((row) => (
        <div className="insight-stat" key={row.label}>
          <small>{row.label}</small>
          <strong>{row.value}</strong>
        </div>
      ))}
    </div>
  );
}
