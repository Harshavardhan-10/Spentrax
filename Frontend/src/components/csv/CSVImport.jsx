import { useRef, useState } from "react";
import Button from "../common/Button";
import ErrorMessage from "../common/ErrorMessage";
import { csvService } from "../../services/csvService";

export default function CSVImport({ onImported }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const handleImport = async () => {
    if (!file) {
      setError("Please choose a CSV file first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const summary = await csvService.import(file);
      setResult(summary);
      if (onImported) onImported();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div className="card">
      <h3>Import expenses from CSV</h3>
      <p className="form-hint">
        Required columns: <code>Date, Description, Merchant, Category, Amount, Payment Method</code>
      </p>
      <div className="csv-import-row">
        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        <Button onClick={handleImport} disabled={loading}>
          {loading ? "Importing…" : "Import CSV"}
        </Button>
      </div>
      <ErrorMessage message={error} />
      {result && (
        <div className="import-summary">
          <div><strong>Total rows</strong><span>{result.total_rows}</span></div>
          <div><strong>Imported</strong><span className="text-success">{result.imported}</span></div>
          <div><strong>Failed</strong><span className="text-danger">{result.failed}</span></div>
          <div><strong>Duplicates</strong><span className="text-warning">{result.duplicates}</span></div>
          {result.errors.length > 0 && (
            <ul className="import-errors">
              {result.errors.slice(0, 10).map((entry) => (
                <li key={entry.row}>
                  Row {entry.row}: {entry.error}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
