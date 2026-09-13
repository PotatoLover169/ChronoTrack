import { useEffect, useMemo, useState } from "react";

import "../../../styles/dashboard.css";
import api from "../../../services/api";
import { useAuthContext } from "../../../hooks/useAuthContext";


function Dashboard() {
  const { user } = useAuthContext();

  const [dashboard, setDashboard] = useState(null);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [currentTimer, setCurrentTimer] = useState(null);

  const [selectedProject, setSelectedProject] = useState("");
  const [description, setDescription] = useState("");

  const [loading, setLoading] = useState(true);
  const [startingTimer, setStartingTimer] = useState(false);
  const [stoppingTimer, setStoppingTimer] = useState(false);

  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState("");


  const loadDashboard = async () => {
    const response = await api.get("dashboard/");
    setDashboard(response.data);
  };


  const loadProjects = async () => {
    const response = await api.get("projects/");
    setProjects(response.data);
  };


  const loadTasks = async () => {
    const response = await api.get("tasks/");
    setTasks(response.data);
  };


  const loadCurrentTimer = async () => {
    try {
      const response = await api.get(
        "tracker/current/"
      );

      setCurrentTimer(response.data);

      if (
        response.data?.elapsed_seconds !==
        undefined
      ) {
        setElapsedSeconds(
          Number(
            response.data.elapsed_seconds || 0
          )
        );
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setCurrentTimer(null);
        setElapsedSeconds(0);
      } else {
        console.error(
          "Failed to load current timer:",
          err
        );
      }
    }
  };


  useEffect(() => {
    const loadData = async () => {
      try {
        setError("");

        await Promise.all([
          loadDashboard(),
          loadProjects(),
          loadTasks(),
          loadCurrentTimer(),
        ]);
      } catch (err) {
        console.error(
          "Failed to load dashboard:",
          err
        );

        setError(
          "Unable to load dashboard data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);


  useEffect(() => {
    if (!currentTimer) {
      return undefined;
    }

    const interval = setInterval(() => {
      setElapsedSeconds(
        (previous) => previous + 1
      );
    }, 1000);

    return () => clearInterval(interval);
  }, [currentTimer]);


  const handleStartTimer = async () => {
    if (!selectedProject) {
      setError(
        "Please select a project first."
      );

      return;
    }

    try {
      setError("");
      setStartingTimer(true);

      await api.post(
        "tracker/start/",
        {
          project: Number(selectedProject),
          description,
        }
      );

      setDescription("");
      setSelectedProject("");

      await Promise.all([
        loadDashboard(),
        loadCurrentTimer(),
      ]);
    } catch (err) {
      console.error(
        "Failed to start timer:",
        err
      );

      if (err.response?.status === 409) {
        setError(
          err.response.data?.detail ||
            "A timer is already running."
        );
      } else {
        setError(
          err.response?.data?.detail ||
            "Unable to start the timer."
        );
      }
    } finally {
      setStartingTimer(false);
    }
  };


  const handleStopTimer = async () => {
    try {
      setError("");
      setStoppingTimer(true);

      await api.post("tracker/stop/");

      setCurrentTimer(null);
      setElapsedSeconds(0);

      await loadDashboard();
    } catch (err) {
      console.error(
        "Failed to stop timer:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Unable to stop the timer."
      );
    } finally {
      setStoppingTimer(false);
    }
  };


  const formatElapsedTime = (seconds) => {
    const totalSeconds = Math.max(
      0,
      Number(seconds || 0)
    );

    const hours = Math.floor(
      totalSeconds / 3600
    );

    const minutes = Math.floor(
      (totalSeconds % 3600) / 60
    );

    const remainingSeconds =
      totalSeconds % 60;

    return [
      hours,
      minutes,
      remainingSeconds,
    ]
      .map((value) =>
        String(value).padStart(2, "0")
      )
      .join(":");
  };


  const getGreeting = () => {
    const hour = new Date().getHours();

    if (hour < 12) {
      return "Good morning";
    }

    if (hour < 18) {
      return "Good afternoon";
    }

    return "Good evening";
  };


  const summary = dashboard?.summary;


  const todayHours = Number(
    summary?.today_hours || 0
  );


  const activeProjectsCount = Number(
    summary?.active_projects || 0
  );


  const openTasks = useMemo(() => {
    return tasks.filter(
      (task) => task.status !== "completed"
    );
  }, [tasks]);


  const activeProjects = useMemo(() => {
    return projects.filter(
      (project) =>
        project.status === "in_progress"
    );
  }, [projects]);


  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-panel-empty">
          Loading dashboard...
        </div>
      </div>
    );
  }


  return (
    <div className="dashboard-page">

      {/* =========================
          PAGE INTRODUCTION
      ========================= */}

      <section className="dashboard-intro">
        <div>
          <p className="dashboard-eyebrow">
            Overview
          </p>

          <h2 className="dashboard-title">
            {getGreeting()}, {user?.username || "there"}
          </h2>

          <p className="dashboard-description">
            Here's an overview of your work and
            productivity.
          </p>
        </div>
      </section>


      {/* =========================
          ERROR
      ========================= */}

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}


      {/* =========================
          SUMMARY
      ========================= */}

      <section className="dashboard-summary">

        <div className="dashboard-summary-card">
          <span>
            Today's Hours
          </span>

          <strong>
            {todayHours.toFixed(2)}h
          </strong>

          <small>
            Tracked today
          </small>
        </div>


        <div className="dashboard-summary-card">
          <span>
            Current Timer
          </span>

          <strong
            className={
              currentTimer
                ? "dashboard-value-running"
                : ""
            }
          >
            {currentTimer
              ? formatElapsedTime(
                  elapsedSeconds
                )
              : "Not running"}
          </strong>

          <small>
            {currentTimer
              ? "Currently tracking"
              : "Ready to start"}
          </small>
        </div>


        <div className="dashboard-summary-card">
          <span>
            Active Projects
          </span>

          <strong>
            {activeProjectsCount}
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
            Tasks remaining
          </small>
        </div>

      </section>


      {/* =========================
          CURRENT TIMER
      ========================= */}

      <section className="dashboard-timer-panel">

        {currentTimer ? (
          <div className="dashboard-running-timer">

            <div className="dashboard-timer-heading">

              <div>
                <p className="dashboard-panel-eyebrow">
                  Time Tracking
                </p>

                <h3>
                  Timer Running
                </h3>

                <p className="dashboard-timer-status">
                  {currentTimer.project?.name ||
                    "Selected project"}
                </p>
              </div>

              <span className="dashboard-timer-badge">
                RUNNING
              </span>

            </div>


            <div className="dashboard-timer-running-content">

              <div>
                <span className="dashboard-timer-label">
                  Current Session
                </span>

                <strong className="dashboard-timer-clock">
                  {formatElapsedTime(
                    elapsedSeconds
                  )}
                </strong>

                <span className="dashboard-timer-description">
                  {currentTimer.description ||
                    "Working session"}
                </span>
              </div>


              <button
                type="button"
                className="dashboard-timer-stop-button"
                onClick={handleStopTimer}
                disabled={stoppingTimer}
              >
                {stoppingTimer
                  ? "Stopping..."
                  : "Stop Timer"}
              </button>

            </div>

          </div>
        ) : (
          <div className="dashboard-timer-content">

            <div>
              <p className="dashboard-panel-eyebrow">
                Time Tracking
              </p>

              <h3>
                Start a Timer
              </h3>

              <p className="dashboard-timer-status">
                Select a project to start tracking
                your work.
              </p>
            </div>


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

                {activeProjects.map(
                  (project) => (
                    <option
                      key={project.id}
                      value={project.id}
                    >
                      {project.name}
                    </option>
                  )
                )}
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

          </div>
        )}

      </section>


      {/* =========================
          MAIN DASHBOARD
      ========================= */}

      <section className="dashboard-grid">

        {/* =====================
            ACTIVE PROJECTS
        ===================== */}

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


          {activeProjects.length > 0 ? (
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


        {/* =====================
            RECENT ACTIVITY
        ===================== */}

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

              {dashboard.recent_entries
                .slice(0, 5)
                .map((entry) => (
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
                ))}

            </div>
          ) : (
            <div className="dashboard-panel-empty">
              No recent activity.
            </div>
          )}

        </div>

      </section>


      {/* =========================
          TODAY'S TASKS
      ========================= */}

      <section className="dashboard-panel dashboard-tasks-panel">

        <div className="dashboard-panel-header">

          <div>
            <p className="dashboard-panel-eyebrow">
              Tasks
            </p>

            <h3>
              Today's Tasks
            </h3>
          </div>

          <span className="dashboard-task-count">
            {openTasks.length} open
          </span>

        </div>


        {openTasks.length > 0 ? (
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
                        "No project"}
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
            No open tasks.
          </div>
        )}

      </section>

    </div>
  );
}


export default Dashboard;