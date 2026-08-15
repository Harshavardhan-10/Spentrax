import Button from "../common/Button";
import { formatCurrency } from "../../utils/formatCurrency";
import { formatDate } from "../../utils/formatDate";
import { FREQUENCIES } from "../../utils/constants";

export default function RecurringList({ items, loading, onToggle, onDelete, onDetect }) {
  return (
    <div>
      <div className="page-toolbar">
        <p>
          Recurring expenses are detected automatically from your transaction history using
          statistical analysis of merchants, amounts and intervals.
        </p>
        <Button onClick={onDetect} disabled={loading}>
          {loading ? "Detecting…" : "Run detection now"}
        </Button>
      </div>

      {items.length === 0 && !loading ? (
        <p className="empty-text">No recurring expenses detected yet. Add a few expenses and run detection.</p>
      ) : (
        <div className="recurring-grid">
          {items.map((item) => (
            <div className="card recurring-card" key={item.id}>
              <div className="recurring-card-header">
                <strong>{item.name}</strong>
                <span className="badge">{item.frequency}</span>
              </div>
              <p className="amount">{formatCurrency(item.amount)}</p>
              <p>
                <small>Next due: {formatDate(item.next_due_date)}</small>
              </p>
              <p>
                <small>Confidence: {(item.confidence_score * 100).toFixed(0)}%</small>
              </p>
              <div className="recurring-card-actions">
                <Button variant="ghost" onClick={() => onToggle(item)}>
                  {item.is_active ? "Disable" : "Enable"}
                </Button>
                <Button variant="danger-ghost" onClick={() => onDelete(item)}>
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
