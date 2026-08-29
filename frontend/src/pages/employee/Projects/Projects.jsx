import { useEffect, useState } from "react";

import api from "../../../services/api";

import "../../../styles/projects.css";

function Projects() {
  const [projects, setProjects] = useState([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("planning");
  const [hourlyRate, setHourlyRate] = useState("");

  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("projects/");

      setProjects(response.data);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to load projects."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setIsSubmitting(true);

    try {
      const response = await api.post("projects/", {
        name,
        description,
        status,
        hourly_rate: hourlyRate || null,
      });

      setProjects((currentProjects) => [
        response.data,
        ...currentProjects,
      ]);

      setName("");
      setDescription("");
      setStatus("planning");
      setHourlyRate("");
    } catch (requestError) {
      const responseData = requestError.response?.data;

      if (responseData) {
        const firstError = Object.values(responseData)[0];

        setError(
          Array.isArray(firstError)
            ? firstError[0]
            : "Unable to create project."
        );
      } else {
        setError("Unable to create project.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="projects-page">
      <div className="projects-header">
        <div>
          <p className="section-label">WORKSPACE</p>

          <h1>Projects</h1>

          <p>
            Manage and organize your projects.
          </p>
        </div>
      </div>

      {error && (
        <div className="projects-error">
          {error}
        </div>
      )}

      {/* Create Project */}
      <div className="projects-card">
        <div className="card-heading">
          <div>
            <p className="section-label">
              NEW PROJECT
            </p>

            <h2>Create a project</h2>
          </div>
        </div>

        <form
          className="project-form"
          onSubmit={handleSubmit}
        >
          <div className="form-field">
            <label htmlFor="project-name">
              Project Name
            </label>

            <input
              id="project-name"
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              placeholder="Enter project name"
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="project-description">
              Description
            </label>

            <textarea
              id="project-description"
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              placeholder="Describe the project"
              rows="3"
            />
          </div>

          <div className="project-form-row">
            <div className="form-field">
              <label htmlFor="project-status">
                Status
              </label>

              <select
                id="project-status"
                value={status}
                onChange={(event) =>
                  setStatus(event.target.value)
                }
              >
                <option value="planning">
                  Planning
                </option>

                <option value="in_progress">
                  In Progress
                </option>

                <option value="on_hold">
                  On Hold
                </option>

                <option value="completed">
                  Completed
                </option>

                <option value="cancelled">
                  Cancelled
                </option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="hourly-rate">
                Hourly Rate
              </label>

              <input
                id="hourly-rate"
                type="number"
                min="0"
                step="0.01"
                value={hourlyRate}
                onChange={(event) =>
                  setHourlyRate(event.target.value)
                }
                placeholder="0.00"
              />
            </div>
          </div>

          <button
            type="submit"
            className="create-project-button"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Creating..."
              : "Create Project"}
          </button>
        </form>
      </div>

      {/* Project List */}
      <div className="projects-card">
        <div className="card-heading">
          <div>
            <p className="section-label">
              PROJECTS
            </p>

            <h2>Your Projects</h2>
          </div>
        </div>

        {loading ? (
          <p className="empty-message">
            Loading projects...
          </p>
        ) : projects.length === 0 ? (
          <p className="empty-message">
            No projects found. Create your first
            project above.
          </p>
        ) : (
          <div className="project-list">
            {projects.map((project) => (
              <div
                className="project-row"
                key={project.id}
              >
                <div className="project-info">
                  <h3>{project.name}</h3>

                  {project.description && (
                    <p>{project.description}</p>
                  )}

                  <span>
                    Created{" "}
                    {new Date(
                      project.created_at
                    ).toLocaleDateString()}
                  </span>
                </div>

                <div className="project-meta">
                  <span
                    className={`project-status status-${project.status}`}
                  >
                    {project.status
                      .replace("_", " ")
                      .toUpperCase()}
                  </span>

                  {project.hourly_rate && (
                    <span className="project-rate">
                      ₱{project.hourly_rate}/hr
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default Projects;