import React from "react";
import { Sparkles, Menu, X } from "lucide-react";

export default function Header({ mobileOpen, setMobileOpen, navItems, activeNav, setActiveNav }) {
  return (
    <header className="topbar">
      <a href="#" className="brand">
        <div className="brand-mark">
          <Sparkles size={20} strokeWidth={2.2} />
        </div>
        <div className="brand-info">
          <span className="brand-title">DocuMind</span>
          <span className="brand-subtitle">Document Intelligence</span>
        </div>
      </a>

      <nav className={`nav ${mobileOpen ? "open" : ""}`}>
        {navItems.map((item) => (
          <button
            key={item}
            className={`nav-link ${activeNav === item ? "active" : ""}`}
            onClick={() => {
              setActiveNav(item);
              setMobileOpen(false);
            }}
          >
            {item}
          </button>
        ))}
      </nav>

      <div className="top-actions">
        <div className="engine-badge" title="Retrieval-Augmented Generation Engine Active">
          <span className="pulse-dot" />
          <span>RAG Engine Ready</span>
        </div>
        <button
          className="mobile-menu-btn"
          onClick={() => setMobileOpen((prev) => !prev)}
          aria-label="Toggle Navigation Menu"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
    </header>
  );
}
