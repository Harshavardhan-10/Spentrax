import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ErrorMessage from "../components/common/ErrorMessage";
import Brand from "../components/common/Brand";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
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
            <h1>Welcome back</h1>
            <p>Login to continue to Spentrax</p>
          </div>
          <form onSubmit={handleSubmit}>
            <label>
              Email
              <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoFocus />
            </label>
            <label>
              Password
              <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
            </label>
            <ErrorMessage message={error} />
            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? "Logging in…" : "Login"}
            </button>
          </form>
          <p className="auth-switch">
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </main>
    </div>
  );
}
