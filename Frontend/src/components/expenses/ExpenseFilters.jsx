import { useApp } from "../../context/AppContext";
import { PAYMENT_METHODS } from "../../utils/constants";
import Button from "../common/Button";

export default function ExpenseFilters({ filters, onChange, onApply, onReset }) {
  const { categories } = useApp();

  const update = (field) => (event) => onChange({ ...filters, [field]: event.target.value || undefined });

  return (
    <div>
      <div className="form-grid">
        <label>
          Search
          <input type="search" placeholder="Description or merchant…" value={filters.search || ""} onChange={update("search")} />
        </label>
        <label>
          Category
          <select value={filters.category || ""} onChange={update("category")}>
            <option value="">All categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Payment method
          <select value={filters.payment_method || ""} onChange={update("payment_method")}>
            <option value="">All methods</option>
            {PAYMENT_METHODS.map((method) => (
              <option key={method} value={method}>
                {method.replace("_", " ")}
              </option>
            ))}
          </select>
        </label>
        <label>
          From date
          <input type="date" value={filters.start_date || ""} onChange={update("start_date")} />
        </label>
        <label>
          To date
          <input type="date" value={filters.end_date || ""} onChange={update("end_date")} />
        </label>
        <label>
          Min amount
          <input type="number" min="0" step="0.01" placeholder="0" value={filters.min_amount || ""} onChange={update("min_amount")} />
        </label>
        <label>
          Max amount
          <input type="number" min="0" step="0.01" placeholder="0" value={filters.max_amount || ""} onChange={update("max_amount")} />
        </label>
        <label>
          Sort by
          <select value={filters.sort_by || "date"} onChange={update("sort_by")}>
            <option value="date">Date</option>
            <option value="amount">Amount</option>
            <option value="description">Description</option>
          </select>
        </label>
        <label>
          Order
          <select value={filters.sort_order || "asc"} onChange={update("sort_order")}>
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </label>
      </div>
      <div className="form-actions">
        <Button variant="ghost" onClick={onReset}>
          Reset
        </Button>
        <Button onClick={onApply}>
          Apply filters
        </Button>
      </div>
    </div>
  );
}