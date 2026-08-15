import Button from "../common/Button";

export default function CategorySuggestion({ suggestion, onAccept, onDismiss }) {
  return (
    <div className="ai-suggestion">
      <div className="ai-suggestion-info">
        <span className="ai-badge">AI</span>
        <div>
          <strong>Suggested category: {suggestion.category}</strong>
          <p>
            Confidence: {(suggestion.confidence * 100).toFixed(0)}% — {suggestion.reason}
          </p>
        </div>
      </div>
      <div className="ai-suggestion-actions">
        <Button onClick={onAccept}>Accept</Button>
        {onDismiss && (
          <Button variant="ghost" onClick={onDismiss}>
            Dismiss
          </Button>
        )}
      </div>
    </div>
  );
}
