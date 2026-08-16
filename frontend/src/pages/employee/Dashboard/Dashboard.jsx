import "../../../styles/dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard-page">
      {/* Page Introduction */}
      <section className="dashboard-intro">
        <div>
          <p className="dashboard-eyebrow">
            Overview
          </p>

          <h2 className="dashboard-title">
            Good morning, Dan
          </h2>

          <p className="dashboard-description">
            Here's an overview of your work and productivity.
          </p>
        </div>
      </section>

      {/* Summary */}
      <section className="dashboard-summary">
        <div className="dashboard-summary-card dashboard-summary-hours">
          <span>Today's Hours</span>

          <strong>06h 24m</strong>

          <small>Tracked today</small>
        </div>

        <div className="dashboard-summary-card dashboard-summary-timer">
          <span>Current Timer</span>

          <strong>Not running</strong>

          <small>Ready to start</small>
        </div>

        <div className="dashboard-summary-card dashboard-summary-projects">
          <span>Active Projects</span>

          <strong>4</strong>

          <small>Currently in progress</small>
        </div>

        <div className="dashboard-summary-card dashboard-summary-tasks">
          <span>Open Tasks</span>

          <strong>12</strong>

          <small>Tasks requiring attention</small>
        </div>
      </section>

      {/* Current Timer */}
      <section className="dashboard-timer-panel">
        <div className="dashboard-timer-content">
          <div>
            <p className="dashboard-panel-eyebrow">
              Time Tracking
            </p>

            <h3>Current Timer</h3>

            <p className="dashboard-timer-status">
              No timer is currently running.
            </p>
          </div>

          <button
            type="button"
            className="dashboard-timer-button"
          >
            Start Timer
          </button>
        </div>
      </section>

      {/* Main Dashboard */}
      <section className="dashboard-grid">
        {/* Recent Activity */}
        <div className="dashboard-panel">
          <div className="dashboard-panel-header">
            <div>
              <p className="dashboard-panel-eyebrow">
                Activity
              </p>

              <h3>Recent Activity</h3>
            </div>
          </div>

          <div className="dashboard-activity-list">
            <div className="dashboard-activity-item">
              <div className="dashboard-activity-indicator" />

              <div className="dashboard-activity-details">
                <strong>Website Development</strong>

                <span>Worked on project tasks</span>
              </div>

              <div className="dashboard-activity-time">
                <strong>02h 15m</strong>

                <span>Today</span>
              </div>
            </div>

            <div className="dashboard-activity-item">
              <div className="dashboard-activity-indicator" />

              <div className="dashboard-activity-details">
                <strong>ChronoTrack</strong>

                <span>Backend API development</span>
              </div>

              <div className="dashboard-activity-time">
                <strong>01h 42m</strong>

                <span>Yesterday</span>
              </div>
            </div>

            <div className="dashboard-activity-item">
              <div className="dashboard-activity-indicator" />

              <div className="dashboard-activity-details">
                <strong>Portfolio</strong>

                <span>Frontend improvements</span>
              </div>

              <div className="dashboard-activity-time">
                <strong>01h 08m</strong>

                <span>Yesterday</span>
              </div>
            </div>
          </div>
        </div>

        {/* Active Projects */}
        <div className="dashboard-panel">
          <div className="dashboard-panel-header">
            <div>
              <p className="dashboard-panel-eyebrow">
                Projects
              </p>

              <h3>Active Projects</h3>
            </div>
          </div>

          <div className="dashboard-panel-empty">
            No active projects.
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;