import { useEffect, useState } from "react";

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
        const [projectsRes, tasksRes, entriesRes] = await Promise.all([
          api.get("projects/"),
          api.get("tasks/"),
          api.get("tracker/"),
        ]);

        setProjects(projectsRes.data);
        setTasks(tasksRes.data);
        setEntries(entriesRes.data);
      } catch (err) {
        console.error(err);
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

  const activeProjects = projects.filter(
    (project) => project.status === "in_progress"
  );

  const openTasks = tasks.filter(
    (task) => task.status !== "completed"
  );

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

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {/* Summary */}
      <section className="dashboard-summary">

        <div className="dashboard-summary-card">
          <span>Active Projects</span>
          <strong>{activeProjects.length}</strong>
          <small>Currently running</small>
        </div>

        <div className="dashboard-summary-card">
          <span>Open Tasks</span>
          <strong>{openTasks.length}</strong>
          <small>Needs attention</small>
        </div>

        <div className="dashboard-summary-card">
          <span>Completed Entries</span>
          <strong>{entries.length}</strong>
          <small>Tracked sessions</small>
        </div>

        <div className="dashboard-summary-card">
          <span>Team Status</span>
          <strong className="dashboard-value-running">
            Active
          </strong>
          <small>Workspace healthy</small>
        </div>

      </section>

      {/* Quick Actions */}
      <section className="dashboard-timer-panel">
        <div className="dashboard-timer-content">

          <div>
            <p className="dashboard-panel-eyebrow">
              Quick Actions
            </p>

            <h3>Manage Your Team</h3>

            <p className="dashboard-timer-status">
              Jump directly into projects, tasks, or reports.
            </p>
          </div>

          <div className="dashboard-timer-controls">

            <button className="dashboard-timer-button">
              View Projects
            </button>

            <button className="dashboard-timer-button">
              View Tasks
            </button>

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

              <h3>Active Projects</h3>
            </div>
          </div>

          {activeProjects.length ? (
            <div className="dashboard-project-list">
              {activeProjects.slice(0, 5).map((project) => (
                <div
                  className="dashboard-project-item"
                  key={project.id}
                >
                  <div className="dashboard-project-details">
                    <strong>{project.name}</strong>

                    <span>
                      {project.client?.name || "No client"}
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

          {entries.length ? (
            <div className="dashboard-activity-list">

              {entries.slice(0, 5).map((entry) => (
                <div
                  className="dashboard-activity-item"
                  key={entry.id}
                >
                  <div className="dashboard-activity-indicator" />

                  <div className="dashboard-activity-details">
                    <strong>{entry.project?.name}</strong>

                    <span>{entry.owner?.username}</span>
                  </div>

                  <div className="dashboard-activity-time">
                    <strong>{entry.duration}</strong>

                    <span>{entry.status}</span>
                  </div>
                </div>
              ))}

            </div>
          ) : (
            <div className="dashboard-panel-empty">
              No recent activity.
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

            <h3>Team Tasks</h3>
          </div>

          <span className="dashboard-task-count">
            {openTasks.length} open
          </span>

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
                  <strong>{task.title}</strong>

                  <span>
                    {task.project?.name || "Project"}
                  </span>
                </div>

                <span
                  className={`dashboard-task-priority dashboard-priority-${task.priority}`}
                >
                  {task.priority}
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