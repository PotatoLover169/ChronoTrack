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
        <div className="dashboard-summary-card">
          <span>Today's Hours</span>
          <strong>06h 24m</strong>
        </div>

        <div className="dashboard-summary-card">
          <span>Current Timer</span>
          <strong>Not running</strong>
        </div>

        <div className="dashboard-summary-card">
          <span>Active Projects</span>
          <strong>4</strong>
        </div>

        <div className="dashboard-summary-card">
          <span>Open Tasks</span>
          <strong>12</strong>
        </div>
      </section>

      {/* Main Dashboard */}
      <section className="dashboard-grid">
        <div className="dashboard-panel">
          <div className="dashboard-panel-header">
            <div>
              <p className="dashboard-panel-eyebrow">
                Activity
              </p>

              <h3>Recent Activity</h3>
            </div>
          </div>

          <div className="dashboard-panel-empty">
            No recent activity.
          </div>
        </div>

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