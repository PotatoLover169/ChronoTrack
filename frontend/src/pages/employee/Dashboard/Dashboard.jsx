import { useEffect, useState } from "react";

import "../../../styles/dashboard.css";
import api from "../../../services/api";

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [projects, setProjects] = useState([]);

  const [selectedProject, setSelectedProject] = useState("");
  const [description, setDescription] = useState("");

  const [loading, setLoading] = useState(true);
  const [startingTimer, setStartingTimer] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = async () => {
    const response = await api.get("dashboard/");
    setDashboard(response.data);
  };

  const loadProjects = async () => {
    const response = await api.get("projects/");
    setProjects(response.data);
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        setError("");

        await Promise.all([
          loadDashboard(),
          loadProjects(),
        ]);
      } catch (err) {
        console.error("Failed to load dashboard:", err);

        setError(
          "Unable to load dashboard data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleStartTimer = async () => {
    if (!selectedProject) {
      setError("Please select a project first.");
      return;
    }

    try {
      setError("");
      setStartingTimer(true);

      await api.post("tracker/start/", {
        project: Number(selectedProject),
        description,
      });

      setDescription("");
      setSelectedProject("");

      await loadDashboard();
    } catch (err) {
      console.error("Failed to start timer:", err);

      if (err.response?.status === 409) {
        setError(
          err.response.data?.detail ||
          "A timer is already running."
        );
      } else {
        setError(
          "Unable to start the timer."
        );
      }
    } finally {
      setStartingTimer(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-panel-empty">
          Loading dashboard...
        </div>
      </div>
    );
  }

  const summary = dashboard?.summary;

  const todayHours =
    Number(summary?.today_hours || 0);

  const activeProjects =
    Number(summary?.active_projects || 0);

  const currentTimer =
    summary?.current_timer;

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

      {/* Error */}
      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {/* Summary */}
      <section className="dashboard-summary">
        <div className="dashboard-summary-card dashboard-summary-hours">
          <span>Today's Hours</span>

          <strong>
            {todayHours.toFixed(2)}h
          </strong>

          <small>
            Tracked today
          </small>
        </div>

        <div className="dashboard-summary-card dashboard-summary-timer">
          <span>Current Timer</span>

          <strong>
            {currentTimer
              ? "Running"
              : "Not running"}
          </strong>

          <small>
            {currentTimer
              ? "Timer is active"
              : "Ready to start"}
          </small>
        </div>

        <div className="dashboard-summary-card dashboard-summary-projects">
          <span>Active Projects</span>

          <strong>
            {activeProjects}
          </strong>

          <small>
            Currently in progress
          </small>
        </div>

        <div className="dashboard-summary-card dashboard-summary-tasks">
          <span>Open Tasks</span>

          <strong>
            —
          </strong>

          <small>
            Coming from task data
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
              {currentTimer
                ? "Timer Running"
                : "Start a Timer"}
            </h3>

            <p className="dashboard-timer-status">
              {currentTimer
                ? `Working on ${
                    currentTimer.project?.name ||
                    "selected project"
                  }`
                : "Select a project to start tracking your work."}
            </p>
          </div>

          {!currentTimer && (
            <div className="dashboard-timer-controls">
              <select
                value={selectedProject}
                onChange={(event) =>
                  setSelectedProject(
                    event.target.value
                  )
                }
                disabled={startingTimer}
              >
                <option value="">
                  Select project
                </option>

                {projects
                  .filter(
                    (project) =>
                      project.status ===
                      "in_progress"
                  )
                  .map((project) => (
                    <option
                      key={project.id}
                      value={project.id}
                    >
                      {project.name}
                    </option>
                  ))}
              </select>

              <input
                type="text"
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value
                  )
                }
                placeholder="What are you working on?"
                disabled={startingTimer}
              />

              <button
                type="button"
                className="dashboard-timer-button"
                onClick={handleStartTimer}
                disabled={startingTimer}
              >
                {startingTimer
                  ? "Starting..."
                  : "Start Timer"}
              </button>
            </div>
          )}
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

          {dashboard?.recent_entries?.length ? (
            <div className="dashboard-activity-list">
              {dashboard.recent_entries.map(
                (entry) => (
                  <div
                    className="dashboard-activity-item"
                    key={entry.id}
                  >
                    <div className="dashboard-activity-indicator" />

                    <div className="dashboard-activity-details">
                      <strong>
                        {entry.project?.name ||
                          "Unknown Project"}
                      </strong>

                      <span>
                        {entry.description ||
                          "Time entry"}
                      </span>
                    </div>

                    <div className="dashboard-activity-time">
                      <strong>
                        {entry.duration ||
                          "—"}
                      </strong>

                      <span>
                        {entry.status}
                      </span>
                    </div>
                  </div>
                )
              )}
            </div>
          ) : (
            <div className="dashboard-panel-empty">
              No recent activity.
            </div>
          )}
        </div>

        {/* Active Projects */}
        <div className="dashboard-panel">
          <div className="dashboard-panel-header">
            <div>
              <p className="dashboard-panel-eyebrow">
                Projects
              </p>

              <h3>
                Active Projects
              </h3>
            </div>
          </div>

          {projects.filter(
            (project) =>
              project.status === "in_progress"
          ).length ? (
            <div className="dashboard-project-list">
              {projects
                .filter(
                  (project) =>
                    project.status ===
                    "in_progress"
                )
                .slice(0, 5)
                .map((project) => (
                  <div
                    className="dashboard-project-item"
                    key={project.id}
                  >
                    <div className="dashboard-project-details">
                      <strong>
                        {project.name}
                      </strong>

                      <span>
                        {project.client?.name ||
                          "No client"}
                      </span>
                    </div>

                    <span className="dashboard-project-status">
                      In Progress
                    </span>
                  </div>
                ))}
            </div>
          ) : (
            <div className="dashboard-panel-empty">
              No active projects.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default Dashboard;