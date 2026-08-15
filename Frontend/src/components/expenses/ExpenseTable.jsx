import { formatCurrency } from "../../utils/formatCurrency";
import { formatDate } from "../../utils/formatDate";
import Button from "../common/Button";

export default function ExpenseTable({ expenses, onEdit, onDelete, showCategory = true }) {
  if (expenses.length === 0) {
    return <p className="empty-text">No expenses found.</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Merchant</th>
            {showCategory && <th>Category</th>}
            <th>Payment</th>
            <th className="align-right">Amount</th>
            <th className="align-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td>{formatDate(expense.expense_date)}</td>
              <td>{expense.description}</td>
              <td>{expense.merchant || "—"}</td>
              {showCategory && <td><span className="badge">{expense.category_name}</span></td>}
              <td>{expense.payment_method.replace("_", " ")}</td>
              <td className="align-right amount">{formatCurrency(expense.amount)}</td>
              <td className="align-right">
                <div className="table-actions">
                  <Button variant="ghost" onClick={() => onEdit(expense)}>
                    Edit
                  </Button>
                  <Button variant="danger-ghost" onClick={() => onDelete(expense)}>
                    Delete
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
