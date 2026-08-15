import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import Brand from "./Brand";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "▦" },
  { to: "/expenses", label: "Expenses", icon: "₹" },
  { to: "/budgets", label: "Budgets", icon: "◫" },
  { to: "/categories", label: "Categories", icon: "▤" },
  { to: "/analytics", label: "Analytics", icon: "◔" },
  { to: "/recurring", label: "Recurring", icon: "↻" },
  { to: "/ai-insights", label: "AI Insights", icon: "✦" },
  { to: "/import-export", label: "Import / Export", icon: "⇅" },
  { to: "/profile", label: "Profile", icon: "●" },
];

export default function Sidebar({ mobile = false, onNavigate }) {
  const { user } = useAuth();

  return (
    <aside className={`sidebar ${mobile ? "sidebar-mobile" : ""}`}>
      <div className="sidebar-brand">
        <Brand light tagline="AI-Powered Expense Tracking" size={34} />
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            onClick={onNavigate}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        {user && (
          <div className="sidebar-user">
            <span className="avatar">{user.name?.charAt(0).toUpperCase() || "U"}</span>
            <div>
              <strong>{user.name}</strong>
              <small>{user.email}</small>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
