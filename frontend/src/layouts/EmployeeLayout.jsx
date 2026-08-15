import { Outlet } from "react-router-dom";
import Sidebar from "../components/navigation/Sidebar";

import "../styles/sidebar.css";
import "../styles/layout.css";

function EmployeeLayout() {
  return (
    <div className="employee-layout">
      <Sidebar />

      <main className="employee-main">
        <Outlet />
      </main>
    </div>
  );
}

export default EmployeeLayout;