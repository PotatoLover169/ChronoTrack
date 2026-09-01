import { Navigate, Outlet } from "react-router-dom";

import useAuth from "../hooks/useAuth";

import EmployeeLayout from "./EmployeeLayout";
import ManagerLayout from "./ManagerLayout";
import AdminLayout from "./AdminLayout";

function RoleBasedLayout() {
  const { user, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === "Employee") {
    return <EmployeeLayout />;
  }

  if (user.role === "Manager") {
    return <ManagerLayout />;
  }

  if (user.role === "Admin") {
    return <AdminLayout />;
  }

  return <Navigate to="/login" replace />;
}

export default RoleBasedLayout;