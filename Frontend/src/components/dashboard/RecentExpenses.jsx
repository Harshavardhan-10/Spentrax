import { formatCurrency } from "../../utils/formatCurrency";
import { formatDate } from "../../utils/formatDate";

export default function RecentExpenses({ expenses }) {
  if (!expenses || expenses.length === 0) {
    return <p className="empty-text">No recent expenses.</p>;
  }

  return (
    <ul className="recent-list">
      {expenses.map((expense) => (
        <li key={expense.id} className="recent-item">
          <div>
            <strong>{expense.description}</strong>
            <small>
              {expense.category_name} · {formatDate(expense.expense_date)}
              {expense.merchant ? ` · ${expense.merchant}` : ""}
            </small>
          </div>
          <span className="amount">{formatCurrency(expense.amount)}</span>
        </li>
      ))}
    </ul>
  );
}
