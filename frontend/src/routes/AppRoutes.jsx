import { Routes, Route } from "react-router-dom";

import EmployeeLayout from "../layouts/EmployeeLayout";
import Dashboard from "../pages/employee/Dashboard/Dashboard";
import Projects from "../pages/employee/Projects/Projects";
import Tasks from "../pages/employee/Tasks/Tasks";
import TimeTracking from "../pages/employee/TimeTracking/TimeTracking";
import Reports from "../pages/employee/Reports/Reports";
import Clients from "../pages/employee/Clients/Clients";

function AppRoutes() {
  return (
    <Routes>
      <Route element={<EmployeeLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/time-tracking" element={<TimeTracking />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/clients" element={<Clients />} />
      </Route>
    </Routes>
  );
}

export default AppRoutes;