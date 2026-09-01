import { Routes, Route } from "react-router-dom";

import EmployeeLayout from "../layouts/EmployeeLayout";
import ManagerLayout from "../layouts/ManagerLayout";
import AdminLayout from "../layouts/AdminLayout";

import RoleBasedLayout from "../layouts/RoleBasedLayout";

import ProtectedRoute from "./ProtectedRoute";
import RoleRoute from "./RoleRoute";

import Login from "../pages/auth/Login/Login";

// Employee pages
import Dashboard from "../pages/employee/Dashboard/Dashboard";
import Projects from "../pages/employee/Projects/Projects";
import Tasks from "../pages/employee/Tasks/Tasks";
import TimeTracking from "../pages/employee/TimeTracking/TimeTracking";
import Reports from "../pages/employee/Reports/Reports";
import Clients from "../pages/employee/Clients/Clients";
import Leave from "../pages/employee/Leave/Leave";

// Manager pages
import ManagerDashboard from "../pages/manager/Dashboard/Dashboard";

// Admin pages
import AdminDashboard from "../pages/admin/Dashboard/Dashboard";

function AppRoutes() {
  return (
    <Routes>

      {/* =====================================================
          AUTHENTICATION
      ===================================================== */}

      <Route
        path="/login"
        element={<Login />}
      />


      {/* =====================================================
          PROTECTED APPLICATION
      ===================================================== */}

      <Route element={<ProtectedRoute />}>


        {/* ===================================================
            EMPLOYEE ROUTES
        =================================================== */}

        <Route
          element={
            <RoleRoute
              allowedRoles={["Employee"]}
            />
          }
        >
          <Route element={<EmployeeLayout />}>

            {/* Employee Dashboard */}
            <Route
              path="/"
              element={<Dashboard />}
            />

            {/* Employee Tasks */}
            <Route
              path="/tasks"
              element={<Tasks />}
            />

            {/* Employee Time Tracking */}
            <Route
              path="/time-tracking"
              element={<TimeTracking />}
            />

            {/* Employee Reports */}
            <Route
              path="/reports"
              element={<Reports />}
            />

            {/* Employee Clients */}
            <Route
              path="/clients"
              element={<Clients />}
            />

            {/* Employee Leave */}
            <Route
              path="/leave"
              element={<Leave />}
            />

          </Route>
        </Route>


        {/* ===================================================
            MANAGER ROUTES
        =================================================== */}

        <Route
          element={
            <RoleRoute
              allowedRoles={["Manager"]}
            />
          }
        >
          <Route element={<ManagerLayout />}>

            {/* Manager Dashboard */}
            <Route
              path="/manager"
              element={<ManagerDashboard />}
            />

            {/* Manager Projects */}
            <Route
              path="/manager/projects"
              element={<Projects />}
            />

            {/* Manager Tasks */}
            <Route
              path="/manager/tasks"
              element={<Tasks />}
            />

            {/* Manager Time Tracking */}
            <Route
              path="/manager/time-tracking"
              element={<TimeTracking />}
            />

            {/* Manager Reports */}
            <Route
              path="/manager/reports"
              element={<Reports />}
            />

            {/* Manager Clients */}
            <Route
              path="/manager/clients"
              element={<Clients />}
            />

            {/* Manager Leave */}
            <Route
              path="/manager/leave"
              element={<Leave />}
            />

          </Route>
        </Route>


        {/* ===================================================
            ADMIN ROUTES
        =================================================== */}

        <Route
          element={
            <RoleRoute
              allowedRoles={["Admin"]}
            />
          }
        >
          <Route element={<AdminLayout />}>

            {/* Admin Dashboard */}
            <Route
              path="/admin"
              element={<AdminDashboard />}
            />

            {/* Admin Projects */}
            <Route
              path="/admin/projects"
              element={<Projects />}
            />

            {/* Admin Tasks */}
            <Route
              path="/admin/tasks"
              element={<Tasks />}
            />

            {/* Admin Clients */}
            <Route
              path="/admin/clients"
              element={<Clients />}
            />

            {/* Admin Reports */}
            <Route
              path="/admin/reports"
              element={<Reports />}
            />

            {/* Admin Time Tracking */}
            <Route
              path="/admin/time-tracking"
              element={<TimeTracking />}
            />

            {/* Admin Leave */}
            <Route
              path="/admin/leave"
              element={<Leave />}
            />

          </Route>
        </Route>

      </Route>

    </Routes>
  );
}

export default AppRoutes;