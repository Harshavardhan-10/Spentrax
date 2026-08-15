import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { AppProvider } from "./context/AppContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Expenses from "./pages/Expenses";
import Budgets from "./pages/Budgets";
import Categories from "./pages/Categories";
import Analytics from "./pages/Analytics";
import RecurringExpenses from "./pages/RecurringExpenses";
import AIInsights from "./pages/AIInsights";
import ImportExport from "./pages/ImportExport";
import Profile from "./pages/Profile";
import Loading from "./components/common/Loading";

function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="page-center">
        <Loading label="Checking session…" />
      </div>
    );
  }
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}

function PublicOnlyRoute() {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="page-center">
        <Loading label="Checking session…" />
      </div>
    );
  }
  return user ? <Navigate to="/dashboard" replace /> : <Outlet />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppProvider>
          <Routes>
            <Route element={<PublicOnlyRoute />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/expenses" element={<Expenses />} />
              <Route path="/budgets" element={<Budgets />} />
              <Route path="/categories" element={<Categories />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/recurring" element={<RecurringExpenses />} />
              <Route path="/ai-insights" element={<AIInsights />} />
              <Route path="/import-export" element={<ImportExport />} />
              <Route path="/profile" element={<Profile />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AppProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
