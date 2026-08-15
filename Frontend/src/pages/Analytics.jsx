import { useEffect, useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import MonthlyChart from "../components/analytics/MonthlyChart";
import CategoryChart from "../components/analytics/CategoryChart";
import TrendChart from "../components/analytics/TrendChart";
import SpendingInsights from "../components/analytics/SpendingInsights";
import { analyticsService } from "../services/analyticsService";

export default function Analytics() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    analyticsService
      .overview({ month, year })
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [month, year]);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Analytics" />
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
          </div>
          {loading && <Loading label="Loading analytics…" />}
          {error && <ErrorMessage message={error} />}
          {data && (
            <>
              <SpendingInsights analytics={data.monthly} />
              <div className="dashboard-grid">
                <div className="card">
                  <h3>Monthly spending (12 months)</h3>
                  <MonthlyChart trends={data.trends} />
                </div>
                <div className="card">
                  <h3>Category breakdown ({month}/{year})</h3>
                  <CategoryChart breakdown={data.categories} />
                </div>
                <div className="card card-wide">
                  <h3>Category trend</h3>
                  <TrendChart
                    data={data.comparison?.categories?.map((item) => item.current)}
                    labels={data.comparison?.categories?.map((item) => item.category)}
                  />
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
