import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../../../services/api";

import "../../../styles/dashboard.css";


function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [entries, setEntries] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setError("");

        const [
          usersResponse,
          projectsResponse,
          tasksResponse,
          entriesResponse,
        ] = await Promise.all([
          api.get("auth/users/"),
          api.get("projects/"),
          api.get("tasks/"),
          api.get("tracker/"),
        ]);

        setUsers(usersResponse.data);
        setProjects(projectsResponse.data);
        setTasks(tasksResponse.data);
        setEntries(entriesResponse.data);
      } catch (requestError) {
        console.error(
          "Failed to load admin dashboard:",
          requestError
        );

        setError(
          requestError.response?.data?.detail ||
            "Unable to load admin dashboard."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);


  /*
   * ---------------------------------------------------------
   * Loading State
   * ---------------------------------------------------------
   */

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
   * ---------------------------------------------------------
   * Organization Calculations
   * ---------------------------------------------------------
   */

  const managers = users.filter(
    (user) => user.role === "Manager"
  );

  const employees = users.filter(
    (user) => user.role === "Employee"
  );

  const activeProjects = projects.filter(
    (project) => project.status === "in_progress"
  );

  const openTasks = tasks.filter(
    (task) => task.status !== "completed"
  );


  /*
   * ---------------------------------------------------------
   * Duration Helpers
   * ---------------------------------------------------------
   */

  const getDurationSeconds = (duration) => {
    if (!duration) {
      return 0;
    }

    const parts = duration.trim().split(" ");

    let days = 0;
    let timePart = "";

    if (parts.length === 2) {
      days = Number(parts[0]) || 0;
      timePart = parts[1];
    } else {
      timePart = parts[0];
    }

    const timeParts = timePart.split(":").map(Number);

    const hours = timeParts[0] || 0;
    const minutes = timeParts[1] || 0;
    const seconds = timeParts[2] || 0;

    return (
      days * 24 * 60 * 60 +
      hours * 60 * 60 +
      minutes * 60 +
      seconds
    );
  };


  const totalTrackedSeconds = entries.reduce(
    (total, entry) => {
      return (
        total +
        getDurationSeconds(entry.duration)
      );
    },
    0
  );

  const totalTrackedHours =
    totalTrackedSeconds / 3600;


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

    const parts = duration.trim().split(" ");

    if (parts.length === 2) {
      const days = Number(parts[0]) || 0;

      const [
        hours = "00",
        minutes = "00",
      ] = parts[1].split(":");

      return `${days}d ${hours}h ${minutes}m`;
    }

    const [
      hours = "00",
      minutes = "00",
    ] = parts[0].split(":");

    return `${Number(hours)}h ${minutes}m`;
  };


  const formatStatus = (status) => {
    if (!status) {
      return "";
    }

    return status
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };


  /*
   * ---------------------------------------------------------
   * Recent Users
   * ---------------------------------------------------------
   */

  const recentUsers = users.slice(0, 5);


  /*
   * ---------------------------------------------------------
   * Recent Activity
   * ---------------------------------------------------------
   */

  const recentEntries = entries.slice(0, 5);


  /*
   * ---------------------------------------------------------
   * Render
   * ---------------------------------------------------------
   */

  return (
    <div className="dashboard-page">

      {/* =====================================================
          INTRO
      ===================================================== */}

      <section className="dashboard-intro">
        <div>
          <p className="dashboard-eyebrow">
            Organization
          </p>

          <h2 className="dashboard-title">
            Admin Dashboard
          </h2>

          <p className="dashboard-description">
            Monitor users, projects, tasks, and
            organization-wide activity.
          </p>
        </div>
      </section>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <section className="dashboard-summary">

        <div className="dashboard-summary-card">
          <span>
            Total Users
          </span>

          <strong>
            {users.length}
          </strong>

          <small>
            Registered accounts
          </small>
        </div>


        <div className="dashboard-summary-card">
          <span>
            Managers
          </span>

          <strong>
            {managers.length}
          </strong>

          <small>
            Management accounts
          </small>
        </div>


        <div className="dashboard-summary-card">
          <span>
            Employees
          </span>

          <strong>
            {employees.length}
          </strong>

          <small>
            Employee accounts
          </small>
        </div>


        <div className="dashboard-summary-card">
          <span>
            Active Projects
          </span>

          <strong>
            {activeProjects.length}
          </strong>

          <small>
            Currently in progress
          </small>
        </div>


        <div className="dashboard-summary-card">
          <span>
            Open Tasks
          </span>

          <strong>
            {openTasks.length}
          </strong>

          <small>
            Tasks still in progress
          </small>
        </div>


        <div className="dashboard-summary-card">
          <span>
            Tracked Hours
          </span>

          <strong>
            {formatHours(totalTrackedHours)}
          </strong>

          <small>
            Total recorded time
          </small>
        </div>

      </section>


      {/* =====================================================
          QUICK ACTIONS
      ===================================================== */}

      <section className="dashboard-timer-panel">

        <div className="dashboard-timer-content">

          <div>
            <p className="dashboard-panel-eyebrow">
              Administration
            </p>

            <h3>
              Manage Organization
            </h3>

            <p className="dashboard-timer-status">
              Access projects, tasks, and organization
              activity from the admin workspace.
            </p>
          </div>


          <div className="dashboard-timer-controls">

            <Link
              to="/admin/projects"
              className="dashboard-timer-button"
            >
              View Projects
            </Link>


            <Link
              to="/admin/tasks"
              className="dashboard-timer-button"
            >
              View Tasks
            </Link>


            <Link
              to="/admin/time-tracking"
              className="dashboard-timer-button"
            >
              View Time Tracking
            </Link>

          </div>

        </div>

      </section>


      {/* =====================================================
          ORGANIZATION OVERVIEW
      ===================================================== */}

      <section className="dashboard-grid">

        {/* ---------------------------------------------------
            USER OVERVIEW
        --------------------------------------------------- */}

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>
              <p className="dashboard-panel-eyebrow">
                Accounts
              </p>

              <h3>
                User Overview
              </h3>
            </div>

            <span className="dashboard-task-count">
              {users.length} total
            </span>

          </div>


          {recentUsers.length ? (
            <div className="dashboard-activity-list">

              {recentUsers.map((user) => (
                <div
                  className="dashboard-activity-item"
                  key={user.id}
                >

                  <div className="dashboard-activity-indicator" />


                  <div className="dashboard-activity-details">

                    <strong>
                      {user.first_name ||
                        user.last_name
                        ? `${user.first_name || ""} ${
                            user.last_name || ""
                          }`.trim()
                        : user.username}
                    </strong>

                    <span>
                      @{user.username}
                    </span>

                  </div>


                  <div className="dashboard-activity-time">

                    <strong>
                      {user.role}
                    </strong>

                    <span>
                      {user.is_active
                        ? "Active"
                        : "Inactive"}
                    </span>

                  </div>

                </div>
              ))}

            </div>
          ) : (
            <div className="dashboard-panel-empty">
              No users found.
            </div>
          )}

        </div>


        {/* ---------------------------------------------------
            PROJECT OVERVIEW
        --------------------------------------------------- */}

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
              to="/admin/projects"
              className="dashboard-task-count"
            >
              View all
            </Link>

          </div>


          {activeProjects.length ? (
            <div className="dashboard-project-list">

              {activeProjects
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

      </section>


      {/* =====================================================
          RECENT ORGANIZATION ACTIVITY
      ===================================================== */}

      <section className="dashboard-panel dashboard-tasks-panel">

        <div className="dashboard-panel-header">

          <div>
            <p className="dashboard-panel-eyebrow">
              Activity
            </p>

            <h3>
              Recent Organization Activity
            </h3>
          </div>

          <span className="dashboard-task-count">
            {entries.length} tracked entries
          </span>

        </div>


        {recentEntries.length ? (
          <div className="dashboard-activity-list">

            {recentEntries.map((entry) => (
              <div
                className="dashboard-activity-item"
                key={entry.id}
              >

                <div className="dashboard-activity-indicator" />


                <div className="dashboard-activity-details">

                  <strong>
                    {entry.project?.name ||
                      "Project"}
                  </strong>

                  <span>
                    {entry.owner?.username ||
                      "User"}

                    {entry.task?.title
                      ? ` · ${entry.task.title}`
                      : ""}

                    {entry.description
                      ? ` · ${entry.description}`
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
            No recent activity.
          </div>
        )}

      </section>


      {/* =====================================================
          TASK OVERVIEW
      ===================================================== */}

      <section className="dashboard-panel dashboard-tasks-panel">

        <div className="dashboard-panel-header">

          <div>
            <p className="dashboard-panel-eyebrow">
              Tasks
            </p>

            <h3>
              Organization Task Overview
            </h3>
          </div>

          <Link
            to="/admin/tasks"
            className="dashboard-task-count"
          >
            {openTasks.length} open
          </Link>

        </div>


        {openTasks.length ? (
          <div className="dashboard-task-list">

            {openTasks
              .slice(0, 6)
              .map((task) => (
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
                      {task.project?.name ||
                        "Project"}

                      {" · "}

                      {task.assigned_to?.username ||
                        "Unassigned"}
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
            No open tasks.
          </div>
        )}

      </section>

    </div>
  );
}


export default AdminDashboard;