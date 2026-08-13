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

          <a href="/">Dashboard</a>
        </div>

        <div>
          <p>Workspace</p>

          <a href="/projects">Projects</a>
          <a href="/tasks">Tasks</a>
          <a href="/time-tracking">Time Tracking</a>
        </div>

        <div>
          <p>Insights</p>

          <a href="/reports">Reports</a>
        </div>

        <div>
          <p>Organization</p>

          <a href="/clients">Clients</a>
          <a href="/leave">Leave</a>
        </div>
      </nav>

      {/* Bottom */}
      <div>
        <a href="/settings">Settings</a>
      </div>
    </aside>
  );
}

export default Sidebar;