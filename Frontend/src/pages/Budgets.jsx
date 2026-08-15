import { useCallback, useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import Modal from "../components/common/Modal";
import Button from "../components/common/Button";
import BudgetForm from "../components/budgets/BudgetForm";
import BudgetCard from "../components/budgets/BudgetCard";
import { budgetService } from "../services/budgetService";
import { useBudgets } from "../hooks/useBudgets";

export default function Budgets() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const { budgets, loading, error, refresh } = useBudgets(month, year);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState("");

  const handleSubmit = useCallback(
    async (payload) => {
      setSubmitting(true);
      setActionError("");
      try {
        if (editing) {
          await budgetService.update(editing.id, payload);
        } else {
          await budgetService.create(payload);
        }
        setModalOpen(false);
        refresh();
      } catch (err) {
        setActionError(err.message);
      } finally {
        setSubmitting(false);
      }
    },
    [editing, refresh]
  );

  const confirmDelete = async () => {
    setSubmitting(true);
    try {
      await budgetService.remove(deleting.id);
      setDeleting(null);
      refresh();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Budgets" />
        <main className="page">
          <div className="page-toolbar">
            <div className="month-picker">
              <select value={month} onChange={(event) => setMonth(parseInt(event.target.value, 10))}>
                {Array.from({ length: 12 }, (_, index) => (
                  <option key={index + 1} value={index + 1}>
                    {new Date(2000, index, 1).toLocaleString("en-IN", { month: "long" })}
                  </option>
                ))}
              </select>
              <input type="number" min="2000" max="2200" value={year} onChange={(event) => setYear(parseInt(event.target.value, 10))} />
            </div>
            <Button onClick={() => { setEditing(null); setActionError(""); setModalOpen(true); }}>
              + Create budget
            </Button>
          </div>
          {loading && <Loading label="Loading budgets…" />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && budgets.length === 0 && (
            <p className="empty-text">No budgets set for this month. Create one to start tracking.</p>
          )}
          <div className="budget-grid">
            {budgets.map((budget) => (
              <BudgetCard
                key={budget.id}
                budget={budget}
                onEdit={(budgetItem) => { setEditing(budgetItem); setActionError(""); setModalOpen(true); }}
                onDelete={setDeleting}
              />
            ))}
          </div>
        </main>
      </div>

      <Modal open={modalOpen} title={editing ? "Edit budget" : "Create budget"} onClose={() => setModalOpen(false)}>
        <ErrorMessage message={actionError} />
        <BudgetForm initial={editing} onSubmit={handleSubmit} onCancel={() => setModalOpen(false)} submitting={submitting} />
      </Modal>

      <Modal open={Boolean(deleting)} title="Delete budget" onClose={() => setDeleting(null)}>
        <p>Delete the {deleting?.category_name} budget for {deleting?.month}/{deleting?.year}?</p>
        <div className="form-actions">
          <Button variant="danger" onClick={confirmDelete} disabled={submitting}>
            {submitting ? "Deleting…" : "Delete"}
          </Button>
          <Button variant="ghost" onClick={() => setDeleting(null)}>
            Cancel
          </Button>
        </div>
      </Modal>
    </div>
  );
}
