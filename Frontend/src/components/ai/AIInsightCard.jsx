import { SEVERITY } from "../../utils/constants";
import { formatDate } from "../../utils/formatDate";

export default function AIInsightCard({ insight }) {
  const severity = SEVERITY[insight.severity] || SEVERITY.INFO;

  return (
    <div className={`card insight-card insight-${insight.insight_type?.toLowerCase()}`}>
      <div className="insight-card-header">
        <div>
          <span className="badge badge-type">{insight.insight_type}</span>
          <strong>{insight.title}</strong>
        </div>
        <span className="severity-dot" style={{ background: severity.color }} title={severity.label} />
      </div>
      <p className="insight-content">{insight.content}</p>
      <small className="insight-date">{formatDate(insight.created_at)}</small>
    </div>
  );
}
