import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside>
      {/* Brand */}
      <div>
        <h1>ChronoTrack</h1>
        <p>Time & Productivity</p>
      </div>

      {/* Navigation */}
      <nav>
        <div>
          <p>Overview</p>

          <NavLink to="/">
            Dashboard
          </NavLink>
        </div>

        <div>
          <p>Workspace</p>

          <NavLink to="/projects">
            Projects
          </NavLink>

          <NavLink to="/tasks">
            Tasks
          </NavLink>

          <NavLink to="/time-tracking">
            Time Tracking
          </NavLink>
        </div>

        <div>
          <p>Insights</p>

          <NavLink to="/reports">
            Reports
          </NavLink>
        </div>

        <div>
          <p>Organization</p>

          <NavLink to="/clients">
            Clients
          </NavLink>

          <NavLink to="/leave">
            Leave
          </NavLink>
        </div>
      </nav>

      {/* Bottom */}
      <div>
        <NavLink to="/settings">
          Settings
        </NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;