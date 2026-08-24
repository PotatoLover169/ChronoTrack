import { Routes, Route } from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";

import EmployeeLayout from "../layouts/EmployeeLayout";

import Dashboard from "../pages/employee/Dashboard/Dashboard";
import Projects from "../pages/employee/Projects/Projects";
import Tasks from "../pages/employee/Tasks/Tasks";
import TimeTracking from "../pages/employee/TimeTracking/TimeTracking";
import Reports from "../pages/employee/Reports/Reports";
import Clients from "../pages/employee/Clients/Clients";
import Leave from "../pages/employee/Leave/Leave";

import Login from "../pages/auth/Login/Login";

function AppRoutes() {
  return (
    <Routes>

      {/* Public Routes */}
      <Route
        path="/login"
        element={<Login />}
      />

      {/* Protected Employee Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<EmployeeLayout />}>

          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/projects"
            element={<Projects />}
          />

          <Route
            path="/tasks"
            element={<Tasks />}
          />

          <Route
            path="/time-tracking"
            element={<TimeTracking />}
          />

          <Route
            path="/reports"
            element={<Reports />}
          />

          <Route
            path="/clients"
            element={<Clients />}
          />

          <Route
            path="/leave"
            element={<Leave />}
          />

        </Route>
      </Route>

    </Routes>
  );
}

export default AppRoutes;