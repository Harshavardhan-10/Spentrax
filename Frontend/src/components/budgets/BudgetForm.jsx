import { useState } from "react";
import Button from "../common/Button";
import { useApp } from "../../context/AppContext";

export default function BudgetForm({ initial, onSubmit, onCancel, submitting }) {
  const { categories } = useApp();
  const [form, setForm] = useState(
    initial
      ? { ...initial, category_id: String(initial.category_id), amount: String(initial.amount) }
      : { category_id: "", amount: "", month: new Date().getMonth() + 1, year: new Date().getFullYear() }
  );
  const [error, setError] = useState("");

  const setField = (field) => (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));

  const handleSubmit = (event) => {
    event.preventDefault();
    setError("");
    if (!form.category_id || !form.amount) {
      setError("Category and amount are required.");
      return;
    }
    onSubmit({
      category_id: parseInt(form.category_id, 10),
      amount: parseFloat(form.amount),
      month: parseInt(form.month, 10),
      year: parseInt(form.year, 10),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <p className="form-error">{error}</p>}
      <div className="form-grid">
        <label>
          Category *
          <select value={form.category_id} onChange={setField("category_id")} required>
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={String(category.id)}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Amount (₹) *
          <input type="number" min="1" step="0.01" value={form.amount} onChange={setField("amount")} required />
        </label>
        <label>
          Month
          <select value={form.month} onChange={setField("month")}>
            {Array.from({ length: 12 }, (_, index) => (
              <option key={index + 1} value={index + 1}>
                {new Date(2000, index, 1).toLocaleString("en-IN", { month: "long" })}
              </option>
            ))}
          </select>
        </label>
        <label>
          Year
          <input type="number" min="2000" max="2200" value={form.year} onChange={setField("year")} />
        </label>
      </div>
      <div className="form-actions">
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving..." : initial ? "Save changes" : "Create budget"}
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
