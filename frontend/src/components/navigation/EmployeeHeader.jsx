import { useLocation } from "react-router-dom";

import useAuth from "../../hooks/useAuth";
import "../../styles/header.css";

function EmployeeHeader() {
  const { user } = useAuth();
  const location = useLocation();

  const role = user?.role || "Employee";

  const pageTitles = {
    "/": "Dashboard",
    "/tasks": "Tasks",
    "/time-tracking": "Time Tracking",
    "/reports": "Reports",
    "/clients": "Clients",
    "/leave": "Leave",
    "/notifications": "Notifications",
    "/settings": "Settings",
  };

  const pageTitle =
    pageTitles[location.pathname] || "Dashboard";

  return (
    <header className="employee-header">
      <div className="employee-header-left">
        <div>
          <p className="employee-header-eyebrow">
            Workspace
          </p>

          <h1 className="employee-header-title">
            {pageTitle}
          </h1>
        </div>
      </div>

      <div className="employee-header-right">
        <span className="employee-header-status">
          {role}
        </span>
      </div>
    </header>
  );
}

export default EmployeeHeader;