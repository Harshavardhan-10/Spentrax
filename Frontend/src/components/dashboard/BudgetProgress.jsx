import { formatCurrency } from "../../utils/formatCurrency";

export default function BudgetProgress({ data }) {
  const percentage = data?.budget_used_percentage ?? 0;
  const color = percentage > 100 ? "#ef4444" : percentage > 90 ? "#f97316" : percentage >= 70 ? "#f59e0b" : "#22c55e";

  return (
    <div className="budget-progress">
      <div className="budget-progress-header">
        <span>Monthly budget utilization</span>
        <strong style={{ color }}>{percentage}%</strong>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${Math.min(percentage, 100)}%`, background: color }} />
      </div>
      <p className="budget-progress-meta">
        Spent {formatCurrency(data?.monthly_expenses ?? 0)} of {formatCurrency(data?.budget ?? 0)} —{" "}
        {formatCurrency(data?.remaining_budget ?? 0)} remaining
      </p>
    </div>
  );
}
