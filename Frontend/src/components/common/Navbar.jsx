import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import Sidebar from "./Sidebar";
import Brand from "./Brand";

export default function Navbar({ title }) {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="navbar">
      <div className="navbar-left">
        <button
          className="hamburger"
          onClick={() => setMenuOpen((open) => !open)}
          aria-label="Toggle navigation"
        >
          ☰
        </button>
        <div className="navbar-brand-chip">
          <Brand size={26} />
        </div>
        <h1>{title || "Spentrax"}</h1>
      </div>
      <div className="navbar-right">
        {user && (
          <span className="navbar-user">
            {user.name} <small>({user.email})</small>
          </span>
        )}
        <button className="btn btn-ghost" onClick={logout}>
          Logout
        </button>
      </div>
      {menuOpen && (
        <div className="navbar-mobile-menu">
          <Sidebar mobile onNavigate={() => setMenuOpen(false)} />
        </div>
      )}
    </header>
  );
}
