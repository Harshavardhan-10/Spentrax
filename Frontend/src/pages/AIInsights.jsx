import { useCallback, useEffect, useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import Button from "../components/common/Button";
import AIInsightCard from "../components/ai/AIInsightCard";
import AIRecommendation from "../components/ai/AIRecommendation";
import SpendingSummary from "../components/ai/SpendingSummary";
import { aiService } from "../services/aiService";

export default function AIInsights() {
  const now = new Date();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  const [insights, setInsights] = useState([]);
  const [summary, setSummary] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const loadAll = useCallback(async () => {
    setError("");
    try {
      const [insightsData, summaryData, recommendationsData, anomaliesData] = await Promise.all([
        aiService.insights(),
        aiService.summary(),
        aiService.recommendations(),
        aiService.anomalies(),
      ]);
      setInsights(insightsData);
      setSummary(summaryData);
      setRecommendations(recommendationsData);
      setAnomalies(anomaliesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const generalInsights = Array.from(
    new Map(
      insights
        .filter((insight) => insight.insight_type !== "MONTHLY_SUMMARY" && insight.insight_type !== "ANOMALY")
        .map((insight) => [insight.title, insight])
    ).values()
  );

  const handleRefresh = async () => {
    setRefreshing(true);
    setError("");
    try {
      await aiService.insights({ refresh: true });
      await loadAll();
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="AI Insights" />
        <main className="page">
          <div className="page-toolbar">
            <Button onClick={handleRefresh} disabled={refreshing}>
              {refreshing ? "Regenerating…" : "Regenerate insights"}
            </Button>
          </div>
          <p className="hint-text">
            Insights are generated locally from your own spending data using statistical analysis, then written in plain
            language. Your data is never sent to third parties unless an AI provider is explicitly configured.
          </p>
          {loading && <Loading label="Loading insights…" />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && (
            <>
              {summary && <SpendingSummary summary={summary} />}
              <div className="dashboard-grid">
                <div className="card">
                  <h3>Recommendations</h3>
                  {recommendations.length === 0 ? (
                    <p className="empty-text">Add more expenses to get budget recommendations.</p>
                  ) : (
                    recommendations.map((recommendation, index) => (
                      <AIRecommendation
                        key={`${recommendation.category}-${index}`}
                        recommendation={recommendation}
                        month={month}
                        year={year}
                      />
                    ))
                  )}
                </div>
                <div className="card">
                  <h3>Anomalies</h3>
                  {anomalies.length === 0 ? (
                    <p className="empty-text">No unusual spending detected.</p>
                  ) : (
                    anomalies.map((anomaly) => (
                      <AIInsightCard key={anomaly.id} insight={anomaly} />
                    ))
                  )}
                </div>
              </div>
              <div className="card">
                <h3>Insights</h3>
{generalInsights.length === 0 ? (
                    <p className="empty-text">No insights yet. Hit “Regenerate insights” to generate them.</p>
                  ) : (
                    generalInsights.map((insight) => <AIInsightCard key={insight.id} insight={insight} />)
                  )}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
