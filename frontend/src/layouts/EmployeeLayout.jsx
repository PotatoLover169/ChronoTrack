import { Outlet } from "react-router-dom";
import Sidebar from "../components/navigation/Sidebar";
import EmployeeHeader from "../components/navigation/EmployeeHeader";

import "../styles/sidebar.css";
import "../styles/layout.css";

function EmployeeLayout() {
  return (
    <div className="employee-layout">
      <Sidebar />

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