import { useLocation } from "react-router-dom";
import "../../styles/header.css";

function ManagerHeader() {
  const location = useLocation();

  const pageTitles = {
    "/manager": "Manager Dashboard",
    "/manager/projects": "Projects",
    "/manager/tasks": "Tasks",
    "/manager/time-tracking": "Time Tracking",
    "/manager/reports": "Reports",
    "/manager/clients": "Clients",
    "/manager/leave": "Leave",
  };

  const pageTitle = pageTitles[location.pathname] || "Manager Dashboard";

  return (
    <header className="employee-header">
      <div className="header-left">
        <span className="header-section-label">Workspace</span>
        <h1>{pageTitle}</h1>
      </div>

      <div className="header-right">
        <span className="header-role">Manager</span>
      </div>
    </header>
  );
}

export default ManagerHeader;