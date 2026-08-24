import { useEffect, useState } from "react";

import api from "../../../services/api";
import "../../../styles/dashboard.css";

function formatHours(hours = 0) {
  const totalMinutes = Math.round(hours * 60);

  const h = Math.floor(totalMinutes / 60);
  const m = totalMinutes % 60;

  return `${String(h).padStart(2, "0")}h ${String(m).padStart(2, "0")}m`;
}

function formatDate(dateString) {
  if (!dateString) {
    return "";
  }

  return new Date(dateString).toLocaleDateString(
    "en-US",
    {
      month: "short",
      day: "numeric",
    }
  );
}

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setError("");

        const response = await api.get("dashboard/");

        setDashboard(response.data);
      } catch (error) {
        console.error(
          "Failed to load dashboard:",
          error
        );

        setError(
          "Unable to load dashboard data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-page">
        <section className="dashboard-intro">
          <div>
            <p className="dashboard-eyebrow">
              Overview
            </p>

            <h2 className="dashboard-title">
              Loading dashboard...
            </h2>

            <p className="dashboard-description">
              Fetching your latest work and productivity data.
            </p>
          </div>
        </section>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="dashboard-page">
        <section className="dashboard-intro">
          <div>
            <p className="dashboard-eyebrow">
              Overview
            </p>

            <h2 className="dashboard-title">
              Dashboard unavailable
            </h2>

            <p className="dashboard-description">
              {error}
            </p>
          </div>
        </section>
      </div>
    );
  }

  const summary = dashboard.summary;

  const recentEntries =
    dashboard.recent_entries || [];

  const topProjects =
    dashboard.top_projects || [];

  const currentTimer =
    summary.current_timer;

  return (
    <div className="dashboard-page">

      {/* Page Introduction */}
      <section className="dashboard-intro">
        <div>
          <p className="dashboard-eyebrow">
            Overview
          </p>

          <h2 className="dashboard-title">
            Good morning
          </h2>

          <p className="dashboard-description">
            Here's an overview of your work and productivity.
          </p>
        </div>
      </section>


      {/* Summary */}
      <section className="dashboard-summary">

        <div className="dashboard-summary-card dashboard-summary-hours">
          <span>
            Today's Hours
          </span>

          <strong>
            {formatHours(summary.today_hours)}
          </strong>

          <small>
            Tracked today
          </small>
        </div>


        <div className="dashboard-summary-card dashboard-summary-timer">
          <span>
            Current Timer
          </span>

          <strong>
            {summary.running_timer
              ? "Running"
              : "Not running"}
          </strong>

          <small>
            {summary.running_timer
              ? currentTimer?.project?.name ||
                "Timer active"
              : "Ready to start"}
          </small>
        </div>


        <div className="dashboard-summary-card dashboard-summary-projects">
          <span>
            Active Projects
          </span>

          <strong>
            {summary.active_projects}
          </strong>

          <small>
            Currently in progress
          </small>
        </div>


        <div className="dashboard-summary-card dashboard-summary-tasks">
          <span>
            Billable Hours
          </span>

          <strong>
            {formatHours(summary.billable_hours)}
          </strong>

          <small>
            Billable work
          </small>
        </div>

      </section>


      {/* Current Timer */}
      <section className="dashboard-timer-panel">
        <div className="dashboard-timer-content">

          <div>
            <p className="dashboard-panel-eyebrow">
              Time Tracking
            </p>

            <h3>
              Current Timer
            </h3>

            {summary.running_timer &&
            currentTimer ? (
              <p className="dashboard-timer-status">
                Working on{" "}
                <strong>
                  {currentTimer.project?.name}
                </strong>
              </p>
            ) : (
              <p className="dashboard-timer-status">
                No timer is currently running.
              </p>
            )}
          </div>

          <button
            type="button"
            className="dashboard-timer-button"
          >
            {summary.running_timer
              ? "View Timer"
              : "Start Timer"}
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

              <h3>
                Recent Activity
              </h3>
            </div>
          </div>


          <div className="dashboard-activity-list">

            {recentEntries.length === 0 ? (
              <p>
                No recent activity.
              </p>
            ) : (
              recentEntries.map((entry) => (
                <div
                  className="dashboard-activity-item"
                  key={entry.id}
                >

                  <div className="dashboard-activity-indicator" />

                  <div className="dashboard-activity-details">

                    <strong>
                      {entry.project?.name ||
                        "No project"}
                    </strong>

                    <span>
                      {entry.description ||
                        entry.task?.title ||
                        "Work session"}
                    </span>

                  </div>


                  <div className="dashboard-activity-time">

                    <strong>
                      {entry.duration
                        ? formatHours(
                            entry.duration / 3600
                          )
                        : "Completed"}
                    </strong>

                    <span>
                      {formatDate(
                        entry.start_time
                      )}
                    </span>

                  </div>

                </div>
              ))
            )}

          </div>

        </div>


        {/* Active Projects */}
        <div className="dashboard-panel">

          <div className="dashboard-panel-header">
            <div>
              <p className="dashboard-panel-eyebrow">
                Projects
              </p>

              <h3>
                Top Projects
              </h3>
            </div>
          </div>


          <div className="dashboard-project-list">

            {topProjects.length === 0 ? (
              <p>
                No project activity yet.
              </p>
            ) : (
              topProjects.map((item) => (
                <div
                  className="dashboard-project-item"
                  key={item.project.id}
                >

                  <div className="dashboard-project-details">

                    <strong>
                      {item.project.name}
                    </strong>

                    <span>
                      {formatHours(item.hours)}
                    </span>

                  </div>

                  <span className="dashboard-project-status">
                    {item.project.status}
                  </span>

                </div>
              ))
            )}

          </div>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;