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

import ManagerDashboard from "../pages/manager/Dashboard/Dashboard";
import AdminDashboard from "../pages/admin/Dashboard/Dashboard";

function AppRoutes() {
  return (
    <Routes>

      {/* ================================
          AUTHENTICATION
      ================================= */}

      <Route
        path="/login"
        element={<Login />}
      />


      {/* ================================
          PROTECTED APPLICATION
      ================================= */}

      <Route element={<ProtectedRoute />}>

        <Route element={<EmployeeLayout />}>

          {/* ================================
              EMPLOYEE DASHBOARD
          ================================= */}

          <Route
            element={
              <RoleRoute
                allowedRoles={["Employee"]}
              />
            }
          >
            <Route
              path="/"
              element={<Dashboard />}
            />
          </Route>


          {/* ================================
              MANAGER DASHBOARD
          ================================= */}

          <Route
            element={
              <RoleRoute
                allowedRoles={["Manager"]}
              />
            }
          >
            <Route
              path="/manager"
              element={<ManagerDashboard />}
            />
          </Route>


          {/* ================================
              ADMIN DASHBOARD
          ================================= */}

          <Route
            element={
              <RoleRoute
                allowedRoles={["Admin"]}
              />
            }
          >
            <Route
              path="/admin"
              element={<AdminDashboard />}
            />
          </Route>


          {/* ================================
              PROJECTS
              Manager + Admin only
          ================================= */}

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


          {/* ================================
              EMPLOYEE ACCESSIBLE PAGES
          ================================= */}

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