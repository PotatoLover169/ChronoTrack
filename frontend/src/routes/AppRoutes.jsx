import { Routes, Route } from "react-router-dom";

import EmployeeLayout from "../layouts/EmployeeLayout";
import Dashboard from "../pages/employee/Dashboard/Dashboard";
import Projects from "../pages/employee/Projects/Projects";
import Tasks from "../pages/employee/Tasks/Tasks";

function AppRoutes() {
  return (
    <Routes>
      <Route element={<EmployeeLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/tasks" element={<Tasks />} />
      </Route>
    </Routes>
  );
}

export default AppRoutes;