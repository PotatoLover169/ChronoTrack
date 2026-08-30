import { Routes, Route } from "react-router-dom";

import EmployeeLayout from "../layouts/EmployeeLayout";

import ProtectedRoute from "./ProtectedRoute";
import RoleRoute from "./RoleRoute";

import Login from "../pages/auth/Login/Login";

import Dashboard from "../pages/employee/Dashboard/Dashboard";
import Projects from "../pages/employee/Projects/Projects";
import Tasks from "../pages/employee/Tasks/Tasks";
import TimeTracking from "../pages/employee/TimeTracking/TimeTracking";
import Reports from "../pages/employee/Reports/Reports";
import Clients from "../pages/employee/Clients/Clients";
import Leave from "../pages/employee/Leave/Leave";

function AppRoutes() {
  return (
    <Routes>

      {/* Authentication */}
      <Route
        path="/login"
        element={<Login />}
      />

      {/* Protected Application */}
      <Route element={<ProtectedRoute />}>

        <Route element={<EmployeeLayout />}>

          {/* Dashboard */}
          <Route
            path="/"
            element={<Dashboard />}
          />

          {/* Manager / Admin only */}
          <Route
            element={
              <RoleRoute
                allowedRoles={["Manager", "Admin"]}
              />
            }
          >
            <Route
              path="/projects"
              element={<Projects />}
            />
          </Route>

          {/* Employee accessible */}
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