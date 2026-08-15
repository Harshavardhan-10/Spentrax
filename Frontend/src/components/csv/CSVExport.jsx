import { useState } from "react";
import Button from "../common/Button";
import { csvService } from "../../services/csvService";

export default function CSVExport() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleExport = async () => {
    setLoading(true);
    setError("");
    try {
      await csvService.export();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Export expenses to CSV</h3>
      <p className="form-hint">
        Download all your expenses with columns: Date, Description, Merchant, Category, Amount, Payment Method.
      </p>
      <Button onClick={handleExport} disabled={loading} variant="secondary">
        {loading ? "Preparing…" : "Download CSV"}
      </Button>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
