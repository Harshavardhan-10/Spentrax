import { useState } from "react";
import Button from "../common/Button";
import { formatCurrency } from "../../utils/formatCurrency";
import { budgetService } from "../../services/budgetService";

export default function AIRecommendation({ recommendation, month, year, onApplied }) {
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState("");
  const [applied, setApplied] = useState(false);

  const apply = async () => {
    if (!recommendation.category_id) {
      setError("This category is no longer available.");
      return;
    }
    setApplying(true);
    setError("");
    try {
      await budgetService.create({
        category_id: recommendation.category_id,
        amount: recommendation.recommended_budget,
        month,
        year,
      });
      setApplied(true);
      if (onApplied) onApplied();
    } catch (err) {
      setError(err.message);
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="card recommendation-card">
      <div className="recommendation-header">
        <strong>{recommendation.category}</strong>
        <span className="amount">{formatCurrency(recommendation.recommended_budget)}</span>
      </div>
      <p>{recommendation.reason}</p>
      {error && <p className="form-error">{error}</p>}
      <div className="form-actions">
        {applied ? (
          <span className="applied-label">Applied</span>
        ) : (
          <Button onClick={apply} disabled={applying}>
            {applying ? "Applying…" : "Apply as budget"}
          </Button>
        )}
      </div>
    </div>
  );
}
