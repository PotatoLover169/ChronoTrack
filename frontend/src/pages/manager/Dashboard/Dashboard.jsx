import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../../../services/api";
import { useAuthContext } from "../../../context/AuthContext";

import "../../../styles/dashboard.css";

function ManagerDashboard() {
  const { user } = useAuthContext();

  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [entries, setEntries] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadData = async () => {
      try {
        setError("");

        const [projectsRes, tasksRes, entriesRes] = await Promise.all([
          api.get("projects/"),
          api.get("tasks/"),
          api.get("tracker/"),
        ]);

        setProjects(projectsRes.data);
        setTasks(tasksRes.data);
        setEntries(entriesRes.data);
      } catch (err) {
        console.error("Failed to load manager dashboard:", err);
        setError("Unable to load manager dashboard.");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-panel-empty">
          Loading dashboard...
        </div>
      </div>
    );
  }

  /*
   * -----------------------------
   * Dashboard calculations
   * -----------------------------
   */

  const activeProjects = projects.filter(
    (project) => project.status === "in_progress"
  );

  const openTasks = tasks.filter(
    (task) => task.status !== "completed"
  );

  const trackedMembers = new Set(
    entries
      .map((entry) => entry.owner?.id)
      .filter(Boolean)
  );

  const totalTeamSeconds = entries.reduce((total, entry) => {
    if (!entry.duration) {
      return total;
    }

    const parts = entry.duration.split(" ");

    let timePart = parts[parts.length - 1];
    let dayPart = 0;

    if (parts.length === 2) {
      dayPart = Number(parts[0]) || 0;
    }

    const [hours = 0, minutes = 0, seconds = 0] =
      timePart.split(":").map(Number);

    return (
      total +
      dayPart * 24 * 60 * 60 +
      hours * 60 * 60 +
      minutes * 60 +
      seconds
    );
  }, 0);

  const totalTeamHours = totalTeamSeconds / 3600;

  /*
   * -----------------------------
   * Helpers
   * -----------------------------
   */

  const formatHours = (hours) => {
    if (!Number.isFinite(hours)) {
      return "0.00 h";
    }

    return `${hours.toFixed(2)} h`;
  };

  const formatDuration = (duration) => {
    if (!duration) {
      return "No duration";
    }

    const parts = duration.split(" ");

    if (parts.length === 2) {
      const days = Number(parts[0]) || 0;
      const [hours, minutes] = parts[1].split(":");

      return `${days}d ${hours}h ${minutes}m`;
    }

    const [hours, minutes] = parts[0].split(":");

    return `${Number(hours)}h ${Number(minutes)}m`;
  };

  const formatStatus = (status) => {
    if (!status) {
      return "";
    }

    return status
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  /*
   * -----------------------------
   * Render
   * -----------------------------
   */

  return (
    <div className="dashboard-page">

      {/* Header */}
      <section className="dashboard-intro">
        <div>
          <p className="dashboard-eyebrow">
            Workspace
          </p>

          <h2 className="dashboard-title">
            Good evening, {user?.first_name || user?.username}
          </h2>

          <p className="dashboard-description">
            Monitor your team's work, projects, and activity.
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

        <div className="dashboard-summary-card">
          <span>Team Hours</span>

          <strong>
            {formatHours(totalTeamHours)}
          </strong>

          <small>
            Total tracked time
          </small>
        </div>

        <div className="dashboard-summary-card">
          <span>Active Projects</span>

          <strong>
            {activeProjects.length}
          </strong>

          <small>
            Currently in progress
          </small>
        </div>

        <div className="dashboard-summary-card">
          <span>Open Tasks</span>

          <strong>
            {openTasks.length}
          </strong>

          <small>
            Needs attention
          </small>
        </div>

        <div className="dashboard-summary-card">
          <span>Tracked Members</span>

          <strong>
            {trackedMembers.size}
          </strong>

          <small>
            Members with tracked time
          </small>
        </div>

      </section>

      {/* Quick Actions */}
      <section className="dashboard-timer-panel">
        <div className="dashboard-timer-content">

          <div>
            <p className="dashboard-panel-eyebrow">
              Quick Actions
            </p>

            <h3>
              Manage Your Team
            </h3>

            <p className="dashboard-timer-status">
              Jump directly into projects, tasks, or reports.
            </p>
          </div>

          <div className="dashboard-timer-controls">

            <Link
              to="/manager/projects"
              className="dashboard-timer-button"
            >
              View Projects
            </Link>

            <Link
              to="/manager/tasks"
              className="dashboard-timer-button"
            >
              View Tasks
            </Link>

          </div>

        </div>
      </section>

      {/* Main Grid */}
      <section className="dashboard-grid">

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

            <Link
              to="/manager/projects"
              className="dashboard-task-count"
            >
              View all
            </Link>
          </div>

          {activeProjects.length ? (
            <div className="dashboard-project-list">

              {activeProjects.slice(0, 5).map((project) => (
                <div
                  className="dashboard-project-item"
                  key={project.id}
                >
                  <div className="dashboard-project-details">

                    <strong>
                      {project.name}
                    </strong>

                    <span>
                      {project.client?.name || "No client"}
                    </span>

                  </div>

                  <span className="dashboard-project-status">
                    {formatStatus(project.status)}
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

        {/* Recent Team Activity */}
        <div className="dashboard-panel">

          <div className="dashboard-panel-header">
            <div>
              <p className="dashboard-panel-eyebrow">
                Activity
              </p>

              <h3>
                Recent Team Activity
              </h3>
            </div>
          </div>

          {entries.length ? (
            <div className="dashboard-activity-list">

              {entries.slice(0, 5).map((entry) => (
                <div
                  className="dashboard-activity-item"
                  key={entry.id}
                >
                  <div className="dashboard-activity-indicator" />

                  <div className="dashboard-activity-details">

                    <strong>
                      {entry.project?.name || "Project"}
                    </strong>

                    <span>
                      {entry.owner?.username || "Team member"}
                      {entry.task?.title
                        ? ` · ${entry.task.title}`
                        : ""}
                    </span>

                  </div>

                  <div className="dashboard-activity-time">

                    <strong>
                      {formatDuration(entry.duration)}
                    </strong>

                    <span>
                      {formatStatus(entry.status)}
                    </span>

                  </div>
                </div>
              ))}

            </div>
          ) : (
            <div className="dashboard-panel-empty">
              No recent team activity.
            </div>
          )}

        </div>

      </section>

      {/* Team Tasks */}
      <section className="dashboard-panel dashboard-tasks-panel">

        <div className="dashboard-panel-header">

          <div>
            <p className="dashboard-panel-eyebrow">
              Tasks
            </p>

            <h3>
              Team Tasks
            </h3>
          </div>

          <Link
            to="/manager/tasks"
            className="dashboard-task-count"
          >
            {openTasks.length} open
          </Link>

        </div>

        {openTasks.length ? (
          <div className="dashboard-task-list">

            {openTasks.slice(0, 6).map((task) => (
              <div
                className="dashboard-task-item"
                key={task.id}
              >
                <div className="dashboard-task-check" />

                <div className="dashboard-task-details">

                  <strong>
                    {task.title}
                  </strong>

                  <span>
                    {task.project?.name || "Project"}
                    {" · "}
                    {task.assigned_to?.username || "Unassigned"}
                  </span>

                </div>

                <span
                  className={`dashboard-task-priority dashboard-priority-${task.priority}`}
                >
                  {formatStatus(task.status)}
                </span>

              </div>
            ))}

          </div>
        ) : (
          <div className="dashboard-panel-empty">
            No pending tasks.
          </div>
        )}

      </section>

    </div>
  );
}

export default ManagerDashboard;