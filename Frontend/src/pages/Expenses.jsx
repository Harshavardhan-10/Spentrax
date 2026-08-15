import { useCallback, useEffect, useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import Modal from "../components/common/Modal";
import Button from "../components/common/Button";
import ExpenseForm from "../components/expenses/ExpenseForm";
import ExpenseTable from "../components/expenses/ExpenseTable";
import ExpenseCard from "../components/expenses/ExpenseCard";
import ExpenseFilters from "../components/expenses/ExpenseFilters";
import { expenseService } from "../services/expenseService";
import { useExpenses } from "../hooks/useExpenses";

export default function Expenses() {
  const [filters, setFilters] = useState({ page: 1, limit: 10 });
  const { items, total, pages, loading, error, refresh } = useExpenses(filters);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState("");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  const activeFilterCount = [
    filters.search,
    filters.category,
    filters.payment_method,
    filters.start_date,
    filters.end_date,
    filters.min_amount,
    filters.max_amount,
    filters.sort_by && filters.sort_by !== "date",
    filters.sort_order && filters.sort_order !== "asc",
  ].filter(Boolean).length;

  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  const openCreate = () => {
    setEditing(null);
    setActionError("");
    setModalOpen(true);
  };

  const openEdit = (expense) => {
    setEditing(expense);
    setActionError("");
    setModalOpen(true);
  };

  const handleSubmit = useCallback(
    async (payload) => {
      setSubmitting(true);
      setActionError("");
      try {
        if (editing) {
          await expenseService.update(editing.id, payload);
        } else {
          await expenseService.create(payload);
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
      await expenseService.remove(deleting.id);
      setDeleting(null);
      refresh();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const resetFilters = () => setFilters({ page: 1, limit: 10 });

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Expenses" />
        <main className="page">
          <div className="page-toolbar">
            <Button onClick={openCreate}>+ Add expense</Button>
            <Button variant="ghost" onClick={() => setFiltersOpen(true)}>
              Filters{activeFilterCount > 0 ? ` (${activeFilterCount})` : ""}
            </Button>
          </div>
          {loading && <Loading label="Loading expenses…" />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && (
            <>
              {isMobile ? (
                <div className="card-grid">
                  {items.map((expense) => (
                    <ExpenseCard key={expense.id} expense={expense} onEdit={openEdit} onDelete={setDeleting} />
                  ))}
                </div>
              ) : (
                <ExpenseTable expenses={items} onEdit={openEdit} onDelete={setDeleting} />
              )}
              {items.length === 0 && <p className="empty-text">No expenses found.</p>}
              {pages > 1 && (
                <div className="pagination">
                  <Button variant="ghost" disabled={filters.page <= 1} onClick={() => setFilters((prev) => ({ ...prev, page: prev.page - 1 }))}>
                    Previous
                  </Button>
                  <span>
                    Page {filters.page} of {pages} · {total} expenses
                  </span>
                  <Button variant="ghost" disabled={filters.page >= pages} onClick={() => setFilters((prev) => ({ ...prev, page: prev.page + 1 }))}>
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      <Modal open={filtersOpen} title="Filter expenses" onClose={() => setFiltersOpen(false)}>
        <ExpenseFilters
          filters={filters}
          onChange={(next) => setFilters({ ...next, page: 1 })}
          onApply={() => setFiltersOpen(false)}
          onReset={() => { resetFilters(); setFiltersOpen(false); }}
        />
      </Modal>

      <Modal open={modalOpen} title={editing ? "Edit expense" : "Add expense"} onClose={() => setModalOpen(false)}>
        <ErrorMessage message={actionError} />
        <ExpenseForm
          initial={editing}
          onSubmit={handleSubmit}
          onCancel={() => setModalOpen(false)}
          submitting={submitting}
        />
      </Modal>

      <Modal open={Boolean(deleting)} title="Delete expense" onClose={() => setDeleting(null)}>
        <p>
          Are you sure you want to delete “{deleting?.description}” ({deleting?.amount})? This cannot be undone.
        </p>
        {actionError && <ErrorMessage message={actionError} />}
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
