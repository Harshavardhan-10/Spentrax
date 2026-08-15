import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { analyticsService } from "../services/analyticsService";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import SummaryCards from "../components/dashboard/SummaryCards";
import SpendingChart from "../components/dashboard/SpendingChart";
import CategoryChart from "../components/dashboard/CategoryChart";
import BudgetProgress from "../components/dashboard/BudgetProgress";
import RecentExpenses from "../components/dashboard/RecentExpenses";
import AIInsightCard from "../components/ai/AIInsightCard";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    analyticsService
      .dashboard()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Dashboard" />
        <main className="page">
          {loading && <Loading label="Loading dashboard…" />}
          {error && <ErrorMessage message={error} />}
          {data && (
            <>
              <SummaryCards data={data} />
              <div className="dashboard-grid">
                <div className="card">
                  <h3>Monthly spending trend</h3>
                  <SpendingChart trend={data.monthly_trend} />
                </div>
                <div className="card">
                  <h3>Category breakdown</h3>
                  <CategoryChart breakdown={data.category_breakdown} />
                </div>
                <div className="card">
                  <h3>Budget</h3>
                  <BudgetProgress data={data} />
                </div>
                <div className="card">
                  <h3>Recent expenses</h3>
                  <RecentExpenses expenses={data.recent_expenses} />
                  <Link className="link-more" to="/expenses">
                    View all expenses →
                  </Link>
                </div>
              </div>
              <div className="dashboard-grid">
                <div className="card">
                  <div className="card-header-row">
                    <h3>AI financial insights</h3>
                    <Link className="link-more" to="/ai-insights">
                      All insights →
                    </Link>
                  </div>
                  {data.ai_insights.length === 0 ? (
                    <p className="empty-text">
                      No insights yet. <Link to="/ai-insights">Generate insights</Link>
                    </p>
                  ) : (
                    data.ai_insights.map((insight) => (
                      <AIInsightCard key={insight.id} insight={insight} />
                    ))
                  )}
                </div>
                <div className="card">
                  <h3>Recurring expenses</h3>
                  {data.recurring_expenses.length === 0 ? (
                    <p className="empty-text">No recurring expenses detected.</p>
                  ) : (
                    <ul className="recent-list">
                      {data.recurring_expenses.map((item) => (
                        <li key={item.id} className="recent-item">
                          <div>
                            <strong>{item.name}</strong>
                            <small>{item.frequency} · {(item.confidence_score * 100).toFixed(0)}% confidence</small>
                          </div>
                          <span className="amount">{item.amount}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                  <Link className="link-more" to="/recurring">
                    Manage recurring expenses →
                  </Link>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
