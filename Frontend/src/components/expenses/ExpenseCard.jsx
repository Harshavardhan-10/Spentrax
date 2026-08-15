import { formatCurrency } from "../../utils/formatCurrency";
import { formatDate } from "../../utils/formatDate";

export default function ExpenseCard({ expense, onEdit, onDelete }) {
  return (
    <div className="card expense-card">
      <div className="expense-card-header">
        <div>
          <strong>{expense.description}</strong>
          <small>{formatDate(expense.expense_date)}</small>
        </div>
        <span className="amount">{formatCurrency(expense.amount)}</span>
      </div>
      <div className="expense-card-meta">
        <span className="badge">{expense.category_name}</span>
        <span>{expense.merchant || "—"}</span>
        <span>{expense.payment_method.replace("_", " ")}</span>
      </div>
      <div className="expense-card-actions">
        <button className="btn btn-ghost" onClick={() => onEdit(expense)}>
          Edit
        </button>
        <button className="btn btn-danger-ghost" onClick={() => onDelete(expense)}>
          Delete
        </button>
      </div>
    </div>
  );
}
