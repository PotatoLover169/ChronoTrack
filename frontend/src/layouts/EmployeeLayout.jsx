import { Outlet } from "react-router-dom";

function EmployeeLayout() {
  return (
    <div>
      <aside>
        Employee Sidebar
      </aside>

      <main>
        <Outlet />
      </main>
    </div>
  );
}

export default EmployeeLayout;