import { BUDGET_STATUS } from "../../utils/constants";

export default function BudgetProgress({ budget }) {
  const status = BUDGET_STATUS[budget.status] || BUDGET_STATUS.HEALTHY;
  const width = Math.min(budget.used_percentage, 100);

  return (
    <div className="budget-progress">
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${width}%`, background: status.color }}
        />
      </div>
      <div className="budget-progress-meta">
        <span>{budget.used_percentage}% used</span>
        <span style={{ color: status.color }}>{status.label}</span>
      </div>
    </div>
  );
}
