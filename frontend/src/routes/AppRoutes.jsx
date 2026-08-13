import { Routes, Route } from "react-router-dom";

import EmployeeLayout from "../layouts/EmployeeLayout";
import Home from "../pages/Home";

function AppRoutes() {
  return (
    <Routes>
      <Route element={<EmployeeLayout />}>
        <Route
          path="/"
          element={<Home />}
        />
      </Route>
    </Routes>
  );
}

export default AppRoutes;