import { useEffect, useRef, useState } from "react";
import Button from "../common/Button";
import CategorySuggestion from "../ai/CategorySuggestion";
import { useApp } from "../../context/AppContext";
import { PAYMENT_METHODS } from "../../utils/constants";
import { todayISO } from "../../utils/formatDate";
import { useAI } from "../../hooks/useAI";

const EMPTY_FORM = {
  amount: "",
  description: "",
  merchant: "",
  category_id: "",
  payment_method: "UPI",
  expense_date: todayISO(),
  notes: "",
};

export default function ExpenseForm({ initial, onSubmit, onCancel, submitting }) {
  const { categories } = useApp();
  const { categorize } = useAI();
  const [form, setForm] = useState(initial ? { ...EMPTY_FORM, ...initial, amount: String(initial.amount) } : EMPTY_FORM);
  const [suggestion, setSuggestion] = useState(null);
  const [suggesting, setSuggesting] = useState(false);
  const [error, setError] = useState("");
  const debounceRef = useRef(null);

  const setField = (field) => (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));

  useEffect(() => {
    const text = `${form.description} ${form.merchant || ""}`.trim();
    if (text.length < 3 || form.category_id) {
      setSuggestion(null);
      return undefined;
    }
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setSuggesting(true);
      try {
        const result = await categorize(form.description, form.merchant);
        setSuggestion(result);
      } catch {
        setSuggestion(null);
      } finally {
        setSuggesting(false);
      }
    }, 600);
    return () => clearTimeout(debounceRef.current);
  }, [form.description, form.merchant, form.category_id, categorize]);

  const acceptSuggestion = () => {
    const category = categories.find((item) => item.name === suggestion.category);
    if (category) {
      setForm((prev) => ({ ...prev, category_id: String(category.id) }));
    }
    setSuggestion(null);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setError("");
    const payload = {
      ...form,
      amount: parseFloat(form.amount),
      category_id: parseInt(form.category_id, 10),
    };
    if (!payload.category_id) {
      setError("Please choose a category.");
      return;
    }
    onSubmit(payload);
  };

  return (
    <form className="expense-form" onSubmit={handleSubmit}>
      {error && <p className="form-error">{error}</p>}
      <div className="form-grid">
        <label>
          Amount (₹) *
          <input type="number" min="0.01" step="0.01" value={form.amount} onChange={setField("amount")} required />
        </label>
        <label>
          Description *
          <input type="text" value={form.description} onChange={setField("description")} required maxLength={255} />
        </label>
        <label>
          Merchant
          <input type="text" value={form.merchant} onChange={setField("merchant")} maxLength={255} />
        </label>
        <label>
          Category *
          <select value={form.category_id} onChange={setField("category_id")} required>
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Payment method
          <select value={form.payment_method} onChange={setField("payment_method")}>
            {PAYMENT_METHODS.map((method) => (
              <option key={method} value={method}>
                {method.replace("_", " ")}
              </option>
            ))}
          </select>
        </label>
        <label>
          Date *
          <input type="date" value={form.expense_date} onChange={setField("expense_date")} required />
        </label>
        <label className="form-grid-full">
          Notes
          <textarea value={form.notes} onChange={setField("notes")} rows={2} />
        </label>
      </div>

      {suggesting && <p className="form-hint">Asking AI for a category suggestion…</p>}
      {suggestion && (
        <CategorySuggestion suggestion={suggestion} onAccept={acceptSuggestion} />
      )}

      <div className="form-actions">
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving..." : initial ? "Save changes" : "Add expense"}
        </Button>
        {onCancel && (
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
