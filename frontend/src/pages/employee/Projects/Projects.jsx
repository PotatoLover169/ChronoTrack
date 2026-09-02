import { useEffect, useState } from "react";

import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";

import "../../../styles/projects.css";

const STATUS_OPTIONS = [
  {
    value: "planning",
    label: "Planning",
  },
  {
    value: "in_progress",
    label: "In Progress",
  },
  {
    value: "on_hold",
    label: "On Hold",
  },
  {
    value: "completed",
    label: "Completed",
  },
  {
    value: "cancelled",
    label: "Cancelled",
  },
];

function Projects() {
  const { user } = useAuth();

  const canManageProjects =
    user?.role === "Manager" || user?.role === "Admin";

  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [clientId, setClientId] = useState("");
  const [status, setStatus] = useState("planning");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [hourlyRate, setHourlyRate] = useState("");

  const [editingProjectId, setEditingProjectId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deletingProjectId, setDeletingProjectId] = useState(null);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    loadProjects();

    if (canManageProjects) {
      loadClients();
    }
  }, [canManageProjects]);

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

  const loadClients = async () => {
    try {
      const response = await api.get("clients/");

      setClients(response.data);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to load clients."
      );
    }
  };

  const resetForm = () => {
    setName("");
    setDescription("");
    setClientId("");
    setStatus("planning");
    setStartDate("");
    setEndDate("");
    setHourlyRate("");
    setEditingProjectId(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!canManageProjects) {
      return;
    }

    setError("");
    setSuccessMessage("");
    setIsSubmitting(true);

    const projectData = {
      name,
      description,
      client_id: clientId,
      status,
      start_date: startDate || null,
      end_date: endDate || null,
      hourly_rate: hourlyRate || "0",
    };

    try {
      if (editingProjectId) {
        const response = await api.patch(
          `projects/${editingProjectId}/`,
          projectData
        );

        setProjects((currentProjects) =>
          currentProjects.map((project) =>
            project.id === editingProjectId
              ? response.data
              : project
          )
        );

        setSuccessMessage(
          "Project updated successfully."
        );
      } else {
        const response = await api.post(
          "projects/",
          projectData
        );

        setProjects((currentProjects) => [
          response.data,
          ...currentProjects,
        ]);

        setSuccessMessage(
          "Project created successfully."
        );
      }

      resetForm();
    } catch (requestError) {
      const responseData = requestError.response?.data;

      if (responseData) {
        const firstError = Object.values(responseData)[0];

        if (Array.isArray(firstError)) {
          setError(firstError[0]);
        } else if (typeof firstError === "string") {
          setError(firstError);
        } else {
          setError(
            editingProjectId
              ? "Unable to update project."
              : "Unable to create project."
          );
        }
      } else {
        setError(
          editingProjectId
            ? "Unable to update project."
            : "Unable to create project."
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (project) => {
    if (!canManageProjects) {
      return;
    }

    setError("");
    setSuccessMessage("");

    setEditingProjectId(project.id);
    setName(project.name || "");
    setDescription(project.description || "");
    setClientId(project.client?.id || "");
    setStatus(project.status || "planning");
    setStartDate(project.start_date || "");
    setEndDate(project.end_date || "");
    setHourlyRate(project.hourly_rate || "");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleDelete = async (project) => {
    if (!canManageProjects) {
      return;
    }

    const confirmed = window.confirm(
      `Are you sure you want to delete "${project.name}"? This action cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccessMessage("");
    setDeletingProjectId(project.id);

    try {
      await api.delete(`projects/${project.id}/`);

      setProjects((currentProjects) =>
        currentProjects.filter(
          (currentProject) =>
            currentProject.id !== project.id
        )
      );

      if (editingProjectId === project.id) {
        resetForm();
      }

      setSuccessMessage(
        "Project deleted successfully."
      );
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to delete project."
      );
    } finally {
      setDeletingProjectId(null);
    }
  };

  const handleCancelEdit = () => {
    resetForm();
    setError("");
    setSuccessMessage("");
  };

  const getStatusLabel = (statusValue) => {
    const statusOption = STATUS_OPTIONS.find(
      (option) => option.value === statusValue
    );

    return statusOption?.label || statusValue;
  };

  const formatDate = (dateValue) => {
    if (!dateValue) {
      return null;
    }

    return new Date(
      `${dateValue}T00:00:00`
    ).toLocaleDateString();
  };

  return (
    <section className="projects-page">
      <div className="projects-header">
        <div>
          <p className="section-label">
            WORKSPACE
          </p>

          <h1>Projects</h1>

          <p>
            {canManageProjects
              ? "Manage and organize your projects."
              : "View the projects assigned to you."}
          </p>
        </div>
      </div>

      {error && (
        <div className="projects-message projects-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="projects-message projects-success">
          {successMessage}
        </div>
      )}

      {/* Create / Edit Project */}
      {canManageProjects && (
        <div className="projects-card">
          <div className="card-heading">
            <div>
              <p className="section-label">
                {editingProjectId
                  ? "EDIT PROJECT"
                  : "NEW PROJECT"}
              </p>

              <h2>
                {editingProjectId
                  ? "Edit project"
                  : "Create a project"}
              </h2>
            </div>

            {editingProjectId && (
              <button
                type="button"
                className="secondary-button"
                onClick={handleCancelEdit}
              >
                Cancel
              </button>
            )}
          </div>

          <form
            className="project-form"
            onSubmit={handleSubmit}
          >
            <div className="project-form-row">
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
                <label htmlFor="project-client">
                  Client
                </label>

                <select
                  id="project-client"
                  value={clientId}
                  onChange={(event) =>
                    setClientId(event.target.value)
                  }
                  required
                >
                  <option value="">
                    Select a client
                  </option>

                  {clients.map((client) => (
                    <option
                      key={client.id}
                      value={client.id}
                    >
                      {client.name}
                    </option>
                  ))}
                </select>
              </div>
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
                  {STATUS_OPTIONS.map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ))}
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

            <div className="project-form-row">
              <div className="form-field">
                <label htmlFor="project-start-date">
                  Start Date
                </label>

                <input
                  id="project-start-date"
                  type="date"
                  value={startDate}
                  onChange={(event) =>
                    setStartDate(event.target.value)
                  }
                />
              </div>

              <div className="form-field">
                <label htmlFor="project-end-date">
                  End Date
                </label>

                <input
                  id="project-end-date"
                  type="date"
                  value={endDate}
                  onChange={(event) =>
                    setEndDate(event.target.value)
                  }
                />
              </div>
            </div>

            <div className="project-form-actions">
              <button
                type="submit"
                className="create-project-button"
                disabled={isSubmitting}
              >
                {isSubmitting
                  ? editingProjectId
                    ? "Saving..."
                    : "Creating..."
                  : editingProjectId
                    ? "Save Changes"
                    : "Create Project"}
              </button>

              {editingProjectId && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleCancelEdit}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>
      )}

      {/* Project List */}
      <div className="projects-card">
        <div className="card-heading">
          <div>
            <p className="section-label">
              PROJECTS
            </p>

            <h2>
              {canManageProjects
                ? "Your Projects"
                : "Assigned Projects"}
            </h2>
          </div>

          {!loading && (
            <span className="project-count">
              {projects.length}{" "}
              {projects.length === 1
                ? "project"
                : "projects"}
            </span>
          )}
        </div>

        {loading ? (
          <div className="projects-state">
            <p>Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="projects-state projects-empty-state">
            <div className="empty-state-icon">
              □
            </div>

            <h3>
              {canManageProjects
                ? "No projects yet"
                : "No projects assigned"}
            </h3>

            <p>
              {canManageProjects
                ? "Create your first project to start organizing work."
                : "Projects assigned to you will appear here."}
            </p>
          </div>
        ) : (
          <div className="project-list">
            {projects.map((project) => (
              <article
                className="project-row"
                key={project.id}
              >
                <div className="project-info">
                  <div className="project-title-row">
                    <h3>{project.name}</h3>

                    <span
                      className={`project-status status-${project.status}`}
                    >
                      {getStatusLabel(
                        project.status
                      )}
                    </span>
                  </div>

                  {project.description && (
                    <p className="project-description">
                      {project.description}
                    </p>
                  )}

                  <div className="project-details">
                    {project.client?.name && (
                      <span>
                        Client:{" "}
                        <strong>
                          {project.client.name}
                        </strong>
                      </span>
                    )}

                    {project.start_date && (
                      <span>
                        Start:{" "}
                        {formatDate(
                          project.start_date
                        )}
                      </span>
                    )}

                    {project.end_date && (
                      <span>
                        End:{" "}
                        {formatDate(
                          project.end_date
                        )}
                      </span>
                    )}
                  </div>
                </div>

                <div className="project-actions">
                  <div className="project-rate">
                    ₱
                    {Number(
                      project.hourly_rate || 0
                    ).toFixed(2)}
                    /hr
                  </div>

                  {canManageProjects && (
                    <div className="project-action-buttons">
                      <button
                        type="button"
                        className="edit-project-button"
                        onClick={() =>
                          handleEdit(project)
                        }
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="delete-project-button"
                        onClick={() =>
                          handleDelete(project)
                        }
                        disabled={
                          deletingProjectId ===
                          project.id
                        }
                      >
                        {deletingProjectId ===
                        project.id
                          ? "Deleting..."
                          : "Delete"}
                      </button>
                    </div>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default Projects;