import { Routes, Route } from "react-router-dom";

import EmployeeLayout from "../layouts/EmployeeLayout";
import ManagerLayout from "../layouts/ManagerLayout";
import AdminLayout from "../layouts/AdminLayout";

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
import Notifications from "../pages/employee/Notifications/Notifications";
import Settings from "../pages/employee/Settings/Settings";

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

      <Route path="/login" element={<Login />} />

      {/* =====================================================
          PROTECTED APPLICATION
      ===================================================== */}

      <Route element={<ProtectedRoute />}>
        {/* ===================================================
            EMPLOYEE ROUTES
        =================================================== */}

        <Route element={<RoleRoute allowedRoles={["Employee"]} />}>
          <Route element={<EmployeeLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/time-tracking" element={<TimeTracking />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/clients" element={<Clients />} />
            <Route path="/leave" element={<Leave />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>

        {/* ===================================================
            MANAGER ROUTES
        =================================================== */}

        <Route element={<RoleRoute allowedRoles={["Manager"]} />}>
          <Route element={<ManagerLayout />}>
            <Route path="/manager" element={<ManagerDashboard />} />
            <Route path="/manager/projects" element={<Projects />} />
            <Route path="/manager/tasks" element={<Tasks />} />
            <Route path="/manager/time-tracking" element={<TimeTracking />} />
            <Route path="/manager/reports" element={<Reports />} />
            <Route path="/manager/clients" element={<Clients />} />
            <Route path="/manager/leave" element={<Leave />} />
            <Route path="/manager/notifications" element={<Notifications />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>

        {/* ===================================================
            ADMIN ROUTES
        =================================================== */}

        <Route element={<RoleRoute allowedRoles={["Admin"]} />}>
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/projects" element={<Projects />} />
            <Route path="/admin/tasks" element={<Tasks />} />
            <Route path="/admin/clients" element={<Clients />} />
            <Route path="/admin/reports" element={<Reports />} />
            <Route path="/admin/time-tracking" element={<TimeTracking />} />
            <Route path="/admin/leave" element={<Leave />} />
            <Route path="/admin/notifications" element={<Notifications />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}

export default AppRoutes;