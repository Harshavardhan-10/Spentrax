import { useCallback, useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import Modal from "../components/common/Modal";
import Button from "../components/common/Button";
import { categoryService } from "../services/categoryService";
import { useApp } from "../context/AppContext";

export default function Categories() {
  const { categories, loadingCategories, refreshCategories } = useApp();
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: "", description: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const openCreate = () => {
    setEditing(null);
    setForm({ name: "", description: "" });
    setError("");
    setModalOpen(true);
  };

  const openEdit = (category) => {
    setEditing(category);
    setForm({ name: category.name, description: category.description || "" });
    setError("");
    setModalOpen(true);
  };

  const handleSubmit = useCallback(
    async (event) => {
      event.preventDefault();
      setSubmitting(true);
      setError("");
      try {
        if (editing) {
          await categoryService.update(editing.id, form);
        } else {
          await categoryService.create(form);
        }
        setModalOpen(false);
        refreshCategories();
      } catch (err) {
        setError(err.message);
      } finally {
        setSubmitting(false);
      }
    },
    [editing, form, refreshCategories]
  );

  const handleDelete = async (category) => {
    if (!window.confirm(`Delete category "${category.name}"?`)) return;
    try {
      await categoryService.remove(category.id);
      refreshCategories();
    } catch (err) {
      window.alert(err.message);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Categories" />
        <main className="page">
          <div className="page-toolbar">
            <Button onClick={openCreate}>+ Add category</Button>
          </div>
          {loadingCategories && <Loading label="Loading categories…" />}
          <div className="card-grid">
            {categories.map((category) => (
              <div className="card category-card" key={category.id}>
                <div className="category-card-header">
                  <strong>{category.name}</strong>
                  {category.is_default ? <span className="badge">Default</span> : <span className="badge badge-custom">Custom</span>}
                </div>
                <p>{category.description || "No description"}</p>
                {!category.is_default && (
                  <div className="category-card-actions">
                    <Button variant="ghost" onClick={() => openEdit(category)}>
                      Edit
                    </Button>
                    <Button variant="danger-ghost" onClick={() => handleDelete(category)}>
                      Delete
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </main>
      </div>

      <Modal open={modalOpen} title={editing ? "Edit category" : "Add category"} onClose={() => setModalOpen(false)}>
        <form onSubmit={handleSubmit}>
          <ErrorMessage message={error} />
          <label>
            Name *
            <input type="text" value={form.name} onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))} required maxLength={100} />
          </label>
          <label>
            Description
            <textarea value={form.description} onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))} rows={2} maxLength={255} />
          </label>
          <div className="form-actions">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Saving…" : "Save"}
            </Button>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
