import { useState } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { Outlet } from "react-router-dom";

export function MainLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <div className="app-shell">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      {mobileOpen && (
        <button
          className="mobile-overlay"
          type="button"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <main className="main-area">
        <Header onMenuOpen={() => setMobileOpen(true)} />
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
