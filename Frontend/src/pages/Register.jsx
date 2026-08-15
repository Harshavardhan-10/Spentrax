import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ErrorMessage from "../components/common/ErrorMessage";
import Brand from "../components/common/Brand";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const setField = (field) => (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (form.password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      await register(form.name, form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <aside className="auth-hero">
        <div className="auth-hero-content">
          <Brand light tagline="Smart Expense Tracking" size={44} />
          <h1>The AI-Powered Partner for Smart Expense Tracking</h1>
          <p className="hero-sub">
            Track expenses, set budgets and get AI-powered insights — all from one private workspace.
          </p>
        </div>
      </aside>

      <main className="auth-form-side">
        <div className="auth-card card">
          <div className="auth-card-header">
            <h1>Create your account</h1>
            <p>Start tracking smarter with Spentrax</p>
          </div>
          <form onSubmit={handleSubmit}>
            <label>
              Name
              <input type="text" value={form.name} onChange={setField("name")} required minLength={2} autoFocus />
            </label>
            <label>
              Email
              <input type="email" value={form.email} onChange={setField("email")} required />
            </label>
            <label>
              Password (min 8 characters)
              <input type="password" value={form.password} onChange={setField("password")} required />
            </label>
            <label>
              Confirm password
              <input type="password" value={form.confirm} onChange={setField("confirm")} required />
            </label>
            <ErrorMessage message={error} />
            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? "Creating account…" : "Register"}
            </button>
          </form>
          <p className="auth-switch">
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </main>
    </div>
  );
}
