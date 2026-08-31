import { useState } from "react";
import { Outlet } from "react-router-dom";

import ManagerSidebar from "../components/navigation/ManagerSidebar";
import ManagerHeader from "../components/navigation/ManagerHeader";

import "../styles/sidebar.css";
import "../styles/layout.css";

function ManagerLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="employee-layout">

      {/* Mobile Menu Button */}
      <button
        type="button"
        className="mobile-menu-button"
        onClick={() => setSidebarOpen(true)}
        aria-label="Open navigation menu"
        aria-expanded={sidebarOpen}
      >
        ☰
      </button>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <button
          type="button"
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close navigation menu"
        />
      )}

      <ManagerSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="employee-main">
        <ManagerHeader />

        <section className="employee-content">
          <Outlet />
        </section>
      </main>

    </div>
  );
}

export default ManagerLayout;