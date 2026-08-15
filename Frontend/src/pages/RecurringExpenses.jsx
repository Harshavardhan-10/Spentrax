import { useCallback, useEffect, useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import Modal from "../components/common/Modal";
import Button from "../components/common/Button";
import RecurringList from "../components/recurring/RecurringList";
import { recurringService } from "../services/recurringService";

export default function RecurringExpenses() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const result = await recurringService.list();
      setItems(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleDetect = async () => {
    setRunning(true);
    setError("");
    try {
      await recurringService.detect();
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  const handleToggle = async (item) => {
    try {
      await recurringService.toggle(item.id, !item.is_active);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  };

  const confirmDelete = async () => {
    setSubmitting(true);
    setError("");
    try {
      await recurringService.remove(deleting.id);
      setDeleting(null);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Recurring Expenses" />
        <main className="page">
          <div className="page-toolbar">
            <Button onClick={handleDetect} disabled={running}>
              {running ? "Scanning…" : "Detect recurring expenses"}
            </Button>
          </div>
          <p className="hint-text">
            The system analyses your expense history for patterns (same merchant, similar amount, regular interval) and
            flags the most confident matches.
          </p>
          {loading && <Loading label="Loading recurring expenses…" />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && (
            <RecurringList items={items} onToggle={handleToggle} onDelete={setDeleting} />
          )}
        </main>
      </div>

      <Modal open={Boolean(deleting)} title="Delete recurring expense" onClose={() => setDeleting(null)}>
        <p>Remove “{deleting?.name}” from your recurring expenses?</p>
        {error && <ErrorMessage message={error} />}
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
