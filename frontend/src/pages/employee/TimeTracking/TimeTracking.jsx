import { useEffect, useState } from "react";

import api from "../../../services/api";

import "../../../styles/time-tracking.css";

function TimeTracking() {
  const [projects, setProjects] = useState([]);
  const [timeEntries, setTimeEntries] = useState([]);
  const [currentTimer, setCurrentTimer] = useState(null);

  const [selectedProject, setSelectedProject] = useState("");
  const [description, setDescription] = useState("");

  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadTimeTrackingData();
  }, []);

  const loadTimeTrackingData = async () => {
    setLoading(true);
    setError("");

    try {
      const [projectsResponse, entriesResponse] =
        await Promise.all([
          api.get("projects/"),
          api.get("tracker/"),
        ]);

      setProjects(projectsResponse.data);
      setTimeEntries(entriesResponse.data);

      try {
        const currentResponse = await api.get(
          "tracker/current/"
        );

        setCurrentTimer(currentResponse.data);
      } catch (currentError) {
        if (currentError.response?.status === 404) {
          setCurrentTimer(null);
        } else {
          throw currentError;
        }
      }
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to load time tracking data."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStartTimer = async (event) => {
    event.preventDefault();

    if (!selectedProject) {
      setError("Please select a project.");
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      await api.post("tracker/start/", {
        project: Number(selectedProject),
        description,
      });

      setDescription("");
      setSelectedProject("");

      await loadTimeTrackingData();
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to start timer."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStopTimer = async () => {
    setError("");
    setIsSubmitting(true);

    try {
      await api.post("tracker/stop/");

      await loadTimeTrackingData();
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to stop timer."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <section className="time-tracking-page">
        <div className="time-tracking-header">
          <p className="section-label">
            TIME TRACKING
          </p>

          <h1>Time Tracking</h1>

          <p>
            Track and manage your working hours.
          </p>
        </div>

        <div className="time-tracking-card">
          Loading time tracking data...
        </div>
      </section>
    );
  }

  return (
    <section className="time-tracking-page">
      {/* Page Header */}
      <div className="time-tracking-header">
        <div>
          <p className="section-label">
            TIME TRACKING
          </p>

          <h1>Time Tracking</h1>

          <p>
            Track and manage your working hours.
          </p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="time-tracking-error">
          {error}
        </div>
      )}

      {/* Current Timer */}
      <div className="time-tracking-card current-timer-card">
        <div className="card-heading">
          <div>
            <p className="section-label">
              CURRENT TIMER
            </p>

            <h2>
              {currentTimer
                ? "Timer Running"
                : "No Active Timer"}
            </h2>
          </div>

          <span
            className={
              currentTimer
                ? "timer-status running"
                : "timer-status"
            }
          >
            {currentTimer ? "RUNNING" : "IDLE"}
          </span>
        </div>

        {currentTimer ? (
          <div className="current-timer-content">
            <div>
              {/* Project */}
              <p className="timer-project">
                {currentTimer.project?.name ||
                  `Project #${currentTimer.project?.id || currentTimer.project}`}
              </p>

              {/* Task */}
              {currentTimer.task && (
                <p className="timer-task">
                  {typeof currentTimer.task === "object"
                    ? currentTimer.task.name ||
                      `Task #${currentTimer.task.id}`
                    : `Task #${currentTimer.task}`}
                </p>
              )}

              {/* Description */}
              {currentTimer.description && (
                <p className="timer-description">
                  {currentTimer.description}
                </p>
              )}

              {/* Start Time */}
              <p className="timer-start">
                Started:{" "}
                {new Date(
                  currentTimer.start_time
                ).toLocaleString()}
              </p>
            </div>

            <button
              type="button"
              className="stop-timer-button"
              onClick={handleStopTimer}
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Stopping..."
                : "Stop Timer"}
            </button>
          </div>
        ) : (
          <p className="empty-message">
            You currently have no running timer.
          </p>
        )}
      </div>

      {/* Start Timer */}
      {!currentTimer && (
        <div className="time-tracking-card">
          <div className="card-heading">
            <div>
              <p className="section-label">
                START TIMER
              </p>

              <h2>Start a new timer</h2>
            </div>
          </div>

          <form
            className="timer-form"
            onSubmit={handleStartTimer}
          >
            {/* Project */}
            <div className="form-field">
              <label htmlFor="project">
                Project
              </label>

              <select
                id="project"
                value={selectedProject}
                onChange={(event) =>
                  setSelectedProject(
                    event.target.value
                  )
                }
                required
              >
                <option value="">
                  Select a project
                </option>

                {projects.map((project) => (
                  <option
                    key={project.id}
                    value={project.id}
                  >
                    {project.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Description */}
            <div className="form-field">
              <label htmlFor="description">
                Description
              </label>

              <input
                id="description"
                type="text"
                value={description}
                onChange={(event) =>
                  setDescription(event.target.value)
                }
                placeholder="What are you working on?"
              />
            </div>

            {/* Start Button */}
            <button
              type="submit"
              className="start-timer-button"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Starting..."
                : "Start Timer"}
            </button>
          </form>
        </div>
      )}

      {/* History */}
      <div className="time-tracking-card">
        <div className="card-heading">
          <div>
            <p className="section-label">
              HISTORY
            </p>

            <h2>Recent Time Entries</h2>
          </div>
        </div>

        {timeEntries.length === 0 ? (
          <p className="empty-message">
            No time entries found.
          </p>
        ) : (
          <div className="time-entry-list">
            {timeEntries.map((entry) => (
              <div
                className="time-entry-row"
                key={entry.id}
              >
                <div>
                  <h3>
                    {entry.project?.name ||
                      `Project #${entry.project?.id || entry.project}`}
                  </h3>

                  {entry.description && (
                    <p>
                      {entry.description}
                    </p>
                  )}

                  <span>
                    {new Date(
                      entry.start_time
                    ).toLocaleString()}
                  </span>
                </div>

                <div className="time-entry-duration">
                  {entry.duration || "Running"}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default TimeTracking;