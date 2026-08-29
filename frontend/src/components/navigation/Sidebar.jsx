import { NavLink } from "react-router-dom";

import "../../styles/sidebar.css";

function Sidebar({ isOpen, onClose }) {
  const handleNavigation = () => {
    if (window.innerWidth <= 768) {
      onClose();
    }
  };

  return (
    <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">
          CT
        </div>

        <div>
          <h1 className="sidebar-brand-name">
            ChronoTrack
          </h1>

          <p className="sidebar-brand-subtitle">
            Time & Productivity
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">

        {/* Overview */}
        <div className="sidebar-section">
          <p className="sidebar-section-label">
            Overview
          </p>

          <NavLink
            to="/"
            onClick={handleNavigation}
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "sidebar-link-active" : ""
              }`
            }
          >
            <span className="sidebar-link-icon">
              □
            </span>

            <span>Dashboard</span>
          </NavLink>
        </div>

        {/* Workspace */}
        <div className="sidebar-section">
          <p className="sidebar-section-label">
            Workspace
          </p>

          {/* Tasks */}
          <NavLink
            to="/tasks"
            onClick={handleNavigation}
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "sidebar-link-active" : ""
              }`
            }
          >
            <span className="sidebar-link-icon">
              ✓
            </span>

            <span>Tasks</span>
          </NavLink>

          {/* Time Tracking */}
          <NavLink
            to="/time-tracking"
            onClick={handleNavigation}
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "sidebar-link-active" : ""
              }`
            }
          >
            <span className="sidebar-link-icon">
              ◷
            </span>

            <span>Time Tracking</span>
          </NavLink>
        </div>

        {/* Insights */}
        <div className="sidebar-section">
          <p className="sidebar-section-label">
            Insights
          </p>

          <NavLink
            to="/reports"
            onClick={handleNavigation}
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "sidebar-link-active" : ""
              }`
            }
          >
            <span className="sidebar-link-icon">
              ≡
            </span>

            <span>Reports</span>
          </NavLink>
        </div>

        {/* Organization */}
        <div className="sidebar-section">
          <p className="sidebar-section-label">
            Organization
          </p>

          <NavLink
            to="/clients"
            onClick={handleNavigation}
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "sidebar-link-active" : ""
              }`
            }
          >
            <span className="sidebar-link-icon">
              ○
            </span>

            <span>Clients</span>
          </NavLink>

          <NavLink
            to="/leave"
            onClick={handleNavigation}
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "sidebar-link-active" : ""
              }`
            }
          >
            <span className="sidebar-link-icon">
              □
            </span>

            <span>Leave</span>
          </NavLink>
        </div>

      </nav>

      {/* Bottom Navigation */}
      <div className="sidebar-bottom">
        <NavLink
          to="/settings"
          onClick={handleNavigation}
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "sidebar-link-active" : ""
            }`
          }
        >
          <span className="sidebar-link-icon">
            ⚙
          </span>

          <span>Settings</span>
        </NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;