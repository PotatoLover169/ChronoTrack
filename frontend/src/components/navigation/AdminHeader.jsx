import { useLocation } from "react-router-dom";
import "../../styles/header.css";

function AdminHeader() {
  const location = useLocation();

  const pageTitles = {
    "/admin": "Admin Dashboard",
    "/admin/projects": "Projects",
    "/admin/tasks": "Tasks",
    "/admin/clients": "Clients",
    "/admin/reports": "Reports",
    "/admin/time-tracking": "Time Tracking",
    "/admin/leave": "Leave",
  };

  const pageTitle = pageTitles[location.pathname] || "Admin Dashboard";

  return (
    <header className="employee-header">
      <div className="header-left">
        <span className="header-section-label">Organization</span>
        <h1>{pageTitle}</h1>
      </div>

      <div className="header-right">
        <span className="header-role">Admin</span>
      </div>
    </header>
  );
}

export default AdminHeader;