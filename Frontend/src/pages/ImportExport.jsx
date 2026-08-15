import { useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import CSVImport from "../components/csv/CSVImport";
import CSVExport from "../components/csv/CSVExport";
import ErrorMessage from "../components/common/ErrorMessage";

export default function ImportExport() {
  const [error, setError] = useState("");

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Import / Export" />
        <main className="page">
          <div className="dashboard-grid">
            <div className="card">
              <h3>Export expenses</h3>
              <p className="hint-text">
                Download all your expenses as a CSV file with headers{" "}
                <code>Date,Description,Merchant,Category,Amount,Payment Method</code>. You can re-import this file
                anytime.
              </p>
              <CSVExport />
            </div>
            <div className="card">
              <h3>Import expenses</h3>
              <p className="hint-text">
                Upload a CSV with the same headers. Categories must match existing ones — unknown categories are
                skipped. Invalid or duplicate rows are reported after import.
              </p>
              <CSVImport onError={setError} />
              <ErrorMessage message={error} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
