import { useEffect, useMemo, useState } from "react";

import api from "../../services/api";
import useAuth from "../../hooks/useAuth";

import "../../styles/tasks.css";


const STATUS_OPTIONS = [
  {
    value: "todo",
    label: "To Do",
  },
  {
    value: "in_progress",
    label: "In Progress",
  },
  {
    value: "completed",
    label: "Completed",
  },
];


const PRIORITY_OPTIONS = [
  {
    value: "low",
    label: "Low",
  },
  {
    value: "medium",
    label: "Medium",
  },
  {
    value: "high",
    label: "High",
  },
];


function TasksPage() {
  const { user } = useAuth();

  const isManager =
    user?.role === "Manager";

  const isAdmin =
    user?.role === "Admin";

  const canManageTasks =
    isManager || isAdmin;


  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [employees, setEmployees] = useState([]);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [projectId, setProjectId] = useState("");
  const [assignedToId, setAssignedToId] = useState("");
  const [priority, setPriority] = useState("medium");
  const [status, setStatus] = useState("todo");
  const [estimatedHours, setEstimatedHours] =
    useState("");
  const [dueDate, setDueDate] = useState("");

  const [editingTaskId, setEditingTaskId] =
    useState(null);

  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] =
    useState(false);
  const [deletingTaskId, setDeletingTaskId] =
    useState(null);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] =
    useState("");


  /*
   * ---------------------------------------------------------
   * Load Data
   * ---------------------------------------------------------
   */

useEffect(() => {
  let cancelled = false;

  const loadData = async () => {
    try {
      const requests = [
        api.get("tasks/"),
        api.get("projects/"),
      ];

      if (canManageTasks) {
        requests.push(
          api.get("auth/users/assignable/")
        );
      }

      const responses = await Promise.all(requests);

      if (cancelled) {
        return;
      }

      setTasks(responses[0].data);
      setProjects(responses[1].data);

      if (canManageTasks) {
        setEmployees(responses[2].data);
      }

      setError("");
    } catch (requestError) {
      if (!cancelled) {
        console.error(
          "Failed to load task data:",
          requestError
        );

        setError(
          requestError.response?.data?.detail ||
            "Unable to load task data."
        );
      }
    } finally {
      if (!cancelled) {
        setLoading(false);
      }
    }
  };

  loadData();

  return () => {
    cancelled = true;
  };
}, [canManageTasks]);

  /*
   * ---------------------------------------------------------
   * Helpers
   * ---------------------------------------------------------
   */

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setProjectId("");
    setAssignedToId("");
    setPriority("medium");
    setStatus("todo");
    setEstimatedHours("");
    setDueDate("");
    setEditingTaskId(null);
  };


  const formatStatus = (statusValue) => {
    const option = STATUS_OPTIONS.find(
      (item) =>
        item.value === statusValue
    );

    return (
      option?.label ||
      statusValue
    );
  };


  const formatPriority = (priorityValue) => {
    const option = PRIORITY_OPTIONS.find(
      (item) =>
        item.value === priorityValue
    );

    return (
      option?.label ||
      priorityValue
    );
  };


  const formatDate = (dateValue) => {
    if (!dateValue) {
      return "No due date";
    }

    return new Date(
      `${dateValue}T00:00:00`
    ).toLocaleDateString();
  };


  const getTaskError = (
    requestError,
    fallback
  ) => {
    const responseData =
      requestError.response?.data;

    if (!responseData) {
      return fallback;
    }

    if (
      typeof responseData.detail ===
      "string"
    ) {
      return responseData.detail;
    }

    const firstError =
      Object.values(responseData)[0];

    if (Array.isArray(firstError)) {
      return firstError[0];
    }

    if (
      typeof firstError ===
      "string"
    ) {
      return firstError;
    }

    return fallback;
  };


  /*
   * ---------------------------------------------------------
   * Task Statistics
   * ---------------------------------------------------------
   */

  const taskStats = useMemo(() => {
    const total = tasks.length;

    const completed = tasks.filter(
      (task) =>
        task.status === "completed"
    ).length;

    const inProgress = tasks.filter(
      (task) =>
        task.status === "in_progress"
    ).length;

    const todo = tasks.filter(
      (task) =>
        task.status === "todo"
    ).length;

    return {
      total,
      completed,
      inProgress,
      todo,
    };
  }, [tasks]);


  /*
   * ---------------------------------------------------------
   * Create / Update
   * ---------------------------------------------------------
   */

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!canManageTasks) {
      return;
    }

    if (!projectId) {
      setError(
        "Please select a project."
      );

      return;
    }

    setError("");
    setSuccessMessage("");
    setIsSubmitting(true);

    const taskData = {
      title,
      description,
      project_id: Number(projectId),
      assigned_to_id:
        assignedToId
          ? Number(assignedToId)
          : null,
      priority,
      status,
      estimated_hours:
        estimatedHours || "0",
      due_date:
        dueDate || null,
    };


    try {
      if (editingTaskId) {
        const response =
          await api.patch(
            `tasks/${editingTaskId}/`,
            taskData
          );

        setTasks(
          (currentTasks) =>
            currentTasks.map(
              (task) =>
                task.id ===
                editingTaskId
                  ? response.data
                  : task
            )
        );

        setSuccessMessage(
          "Task updated successfully."
        );
      } else {
        const response =
          await api.post(
            "tasks/",
            taskData
          );

        setTasks(
          (currentTasks) => [
            response.data,
            ...currentTasks,
          ]
        );

        setSuccessMessage(
          "Task created successfully."
        );
      }

      resetForm();
    } catch (requestError) {
      setError(
        getTaskError(
          requestError,
          editingTaskId
            ? "Unable to update task."
            : "Unable to create task."
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  };


  /*
   * ---------------------------------------------------------
   * Edit
   * ---------------------------------------------------------
   */

  const handleEdit = (task) => {
    if (!canManageTasks) {
      return;
    }

    setError("");
    setSuccessMessage("");

    setEditingTaskId(task.id);

    setTitle(
      task.title || ""
    );

    setDescription(
      task.description || ""
    );

    setProjectId(
      task.project?.id || ""
    );

    setAssignedToId(
      task.assigned_to?.id || ""
    );

    setPriority(
      task.priority || "medium"
    );

    setStatus(
      task.status || "todo"
    );

    setEstimatedHours(
      task.estimated_hours || ""
    );

    setDueDate(
      task.due_date || ""
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };


  /*
   * ---------------------------------------------------------
   * Delete
   * ---------------------------------------------------------
   */

  const handleDelete = async (task) => {
    if (!canManageTasks) {
      return;
    }

    const confirmed =
      window.confirm(
        `Are you sure you want to delete "${task.title}"? This action cannot be undone.`
      );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccessMessage("");
    setDeletingTaskId(task.id);

    try {
      await api.delete(
        `tasks/${task.id}/`
      );

      setTasks(
        (currentTasks) =>
          currentTasks.filter(
            (currentTask) =>
              currentTask.id !==
              task.id
          )
      );

      if (
        editingTaskId === task.id
      ) {
        resetForm();
      }

      setSuccessMessage(
        "Task deleted successfully."
      );
    } catch (requestError) {
      setError(
        getTaskError(
          requestError,
          "Unable to delete task."
        )
      );
    } finally {
      setDeletingTaskId(null);
    }
  };


  /*
   * ---------------------------------------------------------
   * Employee Status Update
   * ---------------------------------------------------------
   */

  const handleStatusChange = async (
    task,
    newStatus
  ) => {
    if (canManageTasks) {
      return;
    }

    if (
      task.status === newStatus
    ) {
      return;
    }

    setError("");
    setSuccessMessage("");

    try {
      const response =
        await api.patch(
          `tasks/${task.id}/`,
          {
            status: newStatus,
          }
        );

      setTasks(
        (currentTasks) =>
          currentTasks.map(
            (currentTask) =>
              currentTask.id ===
              task.id
                ? response.data
                : currentTask
          )
      );

      setSuccessMessage(
        "Task status updated successfully."
      );
    } catch (requestError) {
      setError(
        getTaskError(
          requestError,
          "Unable to update task status."
        )
      );
    }
  };


  /*
   * ---------------------------------------------------------
   * Loading
   * ---------------------------------------------------------
   */

  if (loading) {
    return (
      <section className="tasks-page">

        <div className="tasks-header">
          <div>
            <p className="section-label">
              TASKS
            </p>

            <h1>Tasks</h1>

            <p>
              Loading your tasks...
            </p>
          </div>
        </div>

        <div className="tasks-card">
          Loading tasks...
        </div>

      </section>
    );
  }


  /*
   * ---------------------------------------------------------
   * Render
   * ---------------------------------------------------------
   */

  return (
    <section className="tasks-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="tasks-header">

        <div>
          <p className="section-label">
            TASKS
          </p>

          <h1>Tasks</h1>

          <p>
            {canManageTasks
              ? "Create, assign, and manage organization tasks."
              : "View your assigned tasks and update their status."}
          </p>
        </div>

      </div>


      {/* =====================================================
          MESSAGES
      ===================================================== */}

      {error && (
        <div className="tasks-message tasks-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="tasks-message tasks-success">
          {successMessage}
        </div>
      )}


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <div className="tasks-summary">

        <div className="tasks-summary-card">
          <span>
            Total Tasks
          </span>

          <strong>
            {taskStats.total}
          </strong>

          <small>
            Visible tasks
          </small>
        </div>


        <div className="tasks-summary-card">
          <span>
            To Do
          </span>

          <strong>
            {taskStats.todo}
          </strong>

          <small>
            Not started
          </small>
        </div>


        <div className="tasks-summary-card">
          <span>
            In Progress
          </span>

          <strong>
            {taskStats.inProgress}
          </strong>

          <small>
            Currently active
          </small>
        </div>


        <div className="tasks-summary-card">
          <span>
            Completed
          </span>

          <strong>
            {taskStats.completed}
          </strong>

          <small>
            Finished tasks
          </small>
        </div>

      </div>


      {/* =====================================================
          CREATE / EDIT FORM
      ===================================================== */}

      {canManageTasks && (
        <div className="tasks-card">

          <div className="card-heading">

            <div>

              <p className="section-label">
                {editingTaskId
                  ? "EDIT TASK"
                  : "NEW TASK"}
              </p>

              <h2>
                {editingTaskId
                  ? "Edit task"
                  : "Create a task"}
              </h2>

            </div>


            {editingTaskId && (
              <button
                type="button"
                className="tasks-secondary-button"
                onClick={() => {
                  resetForm();
                  setError("");
                  setSuccessMessage("");
                }}
              >
                Cancel
              </button>
            )}

          </div>


          <form
            className="tasks-form"
            onSubmit={handleSubmit}
          >

            <div className="tasks-form-row">

              <div className="tasks-form-field">

                <label htmlFor="task-title">
                  Task Title
                </label>

                <input
                  id="task-title"
                  type="text"
                  value={title}
                  onChange={(event) =>
                    setTitle(
                      event.target.value
                    )
                  }
                  placeholder="Enter task title"
                  required
                />

              </div>


              <div className="tasks-form-field">

                <label htmlFor="task-project">
                  Project
                </label>

                <select
                  id="task-project"
                  value={projectId}
                  onChange={(event) =>
                    setProjectId(
                      event.target.value
                    )
                  }
                  required
                >

                  <option value="">
                    Select a project
                  </option>

                  {projects.map(
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

              </div>

            </div>


            <div className="tasks-form-field">

              <label htmlFor="task-description">
                Description
              </label>

              <textarea
                id="task-description"
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value
                  )
                }
                placeholder="Describe the task"
                rows="3"
              />

            </div>


            <div className="tasks-form-row">

              <div className="tasks-form-field">

                <label htmlFor="task-assignee">
                  Assign To
                </label>

                <select
                  id="task-assignee"
                  value={assignedToId}
                  onChange={(event) =>
                    setAssignedToId(
                      event.target.value
                    )
                  }
                >

                  <option value="">
                    Unassigned
                  </option>

                  {employees.map(
                    (employee) => (
                      <option
                        key={employee.id}
                        value={employee.id}
                      >
                        {employee.first_name ||
                        employee.last_name
                          ? `${employee.first_name || ""} ${
                              employee.last_name || ""
                            }`.trim()
                          : employee.username}
                      </option>
                    )
                  )}

                </select>

              </div>


              <div className="tasks-form-field">

                <label htmlFor="task-priority">
                  Priority
                </label>

                <select
                  id="task-priority"
                  value={priority}
                  onChange={(event) =>
                    setPriority(
                      event.target.value
                    )
                  }
                >

                  {PRIORITY_OPTIONS.map(
                    (option) => (
                      <option
                        key={option.value}
                        value={option.value}
                      >
                        {option.label}
                      </option>
                    )
                  )}

                </select>

              </div>

            </div>


            <div className="tasks-form-row">

              <div className="tasks-form-field">

                <label htmlFor="task-status">
                  Status
                </label>

                <select
                  id="task-status"
                  value={status}
                  onChange={(event) =>
                    setStatus(
                      event.target.value
                    )
                  }
                >

                  {STATUS_OPTIONS.map(
                    (option) => (
                      <option
                        key={option.value}
                        value={option.value}
                      >
                        {option.label}
                      </option>
                    )
                  )}

                </select>

              </div>


              <div className="tasks-form-field">

                <label htmlFor="task-estimated-hours">
                  Estimated Hours
                </label>

                <input
                  id="task-estimated-hours"
                  type="number"
                  min="0"
                  step="0.25"
                  value={estimatedHours}
                  onChange={(event) =>
                    setEstimatedHours(
                      event.target.value
                    )
                  }
                  placeholder="0.00"
                />

              </div>

            </div>


            <div className="tasks-form-row">

              <div className="tasks-form-field">

                <label htmlFor="task-due-date">
                  Due Date
                </label>

                <input
                  id="task-due-date"
                  type="date"
                  value={dueDate}
                  onChange={(event) =>
                    setDueDate(
                      event.target.value
                    )
                  }
                />

              </div>

            </div>


            <div className="tasks-form-actions">

              <button
                type="submit"
                className="tasks-primary-button"
                disabled={isSubmitting}
              >
                {isSubmitting
                  ? "Saving..."
                  : editingTaskId
                    ? "Update Task"
                    : "Create Task"}
              </button>

            </div>

          </form>

        </div>
      )}


      {/* =====================================================
          TASK LIST
      ===================================================== */}

      <div className="tasks-card">

        <div className="card-heading">

          <div>

            <p className="section-label">
              {canManageTasks
                ? "ORGANIZATION TASKS"
                : "MY TASKS"}
            </p>

            <h2>
              {canManageTasks
                ? "Task Management"
                : "Assigned Tasks"}
            </h2>

          </div>

          <span className="tasks-count">
            {tasks.length} tasks
          </span>

        </div>


        {tasks.length ? (

          <div className="tasks-list">

            {tasks.map((task) => (

              <div
                className="task-row"
                key={task.id}
              >

                <div className="task-main">

                  <div className="task-title-row">

                    <h3>
                      {task.title}
                    </h3>

                    <span
                      className={`task-priority task-priority-${task.priority}`}
                    >
                      {formatPriority(
                        task.priority
                      )}
                    </span>

                  </div>


                  {task.description && (
                    <p className="task-description">
                      {task.description}
                    </p>
                  )}


                  <div className="task-meta">

                    <span>
                      Project:{" "}
                      <strong>
                        {task.project?.name ||
                          "Unknown"}
                      </strong>
                    </span>

                    <span>
                      Assigned to:{" "}
                      <strong>
                        {task.assigned_to
                          ?.username ||
                          "Unassigned"}
                      </strong>
                    </span>

                    <span>
                      Due:{" "}
                      <strong>
                        {formatDate(
                          task.due_date
                        )}
                      </strong>
                    </span>

                    <span>
                      Estimate:{" "}
                      <strong>
                        {task.estimated_hours ||
                          "0.00"}{" "}
                        h
                      </strong>
                    </span>

                  </div>

                </div>


                <div className="task-actions">

                  {canManageTasks ? (

                    <>

                      <span
                        className={`task-status task-status-${task.status}`}
                      >
                        {formatStatus(
                          task.status
                        )}
                      </span>

                      <div className="task-action-buttons">

                        <button
                          type="button"
                          className="tasks-edit-button"
                          onClick={() =>
                            handleEdit(task)
                          }
                        >
                          Edit
                        </button>


                        <button
                          type="button"
                          className="tasks-delete-button"
                          onClick={() =>
                            handleDelete(task)
                          }
                          disabled={
                            deletingTaskId ===
                            task.id
                          }
                        >
                          {deletingTaskId ===
                          task.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>

                      </div>

                    </>

                  ) : (

                    <div className="task-status-control">

                      <label
                        htmlFor={`task-status-${task.id}`}
                      >
                        Status
                      </label>

                      <select
                        id={`task-status-${task.id}`}
                        value={task.status}
                        onChange={(event) =>
                          handleStatusChange(
                            task,
                            event.target.value
                          )
                        }
                      >

                        {STATUS_OPTIONS.map(
                          (option) => (
                            <option
                              key={
                                option.value
                              }
                              value={
                                option.value
                              }
                            >
                              {option.label}
                            </option>
                          )
                        )}

                      </select>

                    </div>

                  )}

                </div>

              </div>

            ))}

          </div>

        ) : (

          <div className="tasks-empty-state">

            <h3>
              No tasks found
            </h3>

            <p>
              {canManageTasks
                ? "Create your first task to start organizing work."
                : "You currently have no tasks assigned to you."}
            </p>

          </div>

        )}

      </div>

    </section>
  );
}


export default TasksPage;