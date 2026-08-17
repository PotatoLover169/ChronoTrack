import { useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "../components/navigation/Sidebar";
import EmployeeHeader from "../components/navigation/EmployeeHeader";

import "../styles/sidebar.css";
import "../styles/layout.css";

function EmployeeLayout() {
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

      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="employee-main">
        <EmployeeHeader />

        <section className="employee-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default EmployeeLayout;