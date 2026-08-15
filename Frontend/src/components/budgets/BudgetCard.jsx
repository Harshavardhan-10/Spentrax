import BudgetProgress from "./BudgetProgress";
import Button from "../common/Button";
import { formatCurrency } from "../../utils/formatCurrency";

export default function BudgetCard({ budget, onEdit, onDelete }) {
  return (
    <div className="card budget-card">
      <div className="budget-card-header">
        <div className="budget-card-title">
          <strong>{budget.category_name}</strong>
          <small>
            {new Date(2000, budget.month - 1, 1).toLocaleString("en-IN", { month: "long" })} {budget.year}
          </small>
        </div>
        <span className={`badge badge-status badge-${budget.status?.toLowerCase()}`}>
          {budget.status}
        </span>
      </div>
      <div className="budget-card-numbers">
        <div className="budget-stat">
          <small>Budget</small>
          <strong>{formatCurrency(budget.amount)}</strong>
        </div>
        <div className="budget-stat">
          <small>Spent</small>
          <strong>{formatCurrency(budget.spent)}</strong>
        </div>
        <div className="budget-stat">
          <small>Remaining</small>
          <strong>{formatCurrency(budget.remaining)}</strong>
        </div>
      </div>
      <BudgetProgress budget={budget} />
      <div className="budget-card-actions">
        <Button variant="ghost" onClick={() => onEdit(budget)}>
          Edit
        </Button>
        <Button variant="danger-ghost" onClick={() => onDelete(budget)}>
          Delete
        </Button>
      </div>
    </div>
  );
}
