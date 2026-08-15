export default function SpendingSummary({ summary, loading }) {
  if (loading) return <p className="form-hint">Generating your monthly financial summary…</p>;
  if (!summary) return null;

  return (
    <div className="card summary-banner">
      <h3>Monthly Financial Summary</h3>
      <p>{summary.summary}</p>
    </div>
  );
}
