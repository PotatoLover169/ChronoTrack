
import { useEffect, useMemo, useState } from "react";

import api from "../../../services/api";
import "../../../styles/notifications.css";

function getNotifications(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
}

function getErrorMessage(error, fallback) {
  const data = error?.response?.data;

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  if (typeof data?.message === "string") {
    return data.message;
  }

  return fallback;
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function getTypeLabel(type) {
  const labels = {
    timer: "Time tracking",
    task: "Task",
    project: "Project",
    approval: "Approval",
    system: "System",
  };

  return labels[type] || "Notification";
}

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [busyIds, setBusyIds] = useState([]);
  const [markingAll, setMarkingAll] = useState(false);
  const [deletingIds, setDeletingIds] = useState([]);

  useEffect(() => {
    let cancelled = false;

    async function fetchNotifications() {
      try {
        const response = await api.get("notifications/");

        if (cancelled) {
          return;
        }

        setNotifications(getNotifications(response.data));
        setError("");
      } catch (requestError) {
        if (!cancelled) {
          setError(
            getErrorMessage(
              requestError,
              "Unable to load notifications. Please try again.",
            ),
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchNotifications();

    return () => {
      cancelled = true;
    };
  }, []);

  const unreadCount = useMemo(
    () => notifications.filter((item) => !item.is_read).length,
    [notifications],
  );

  const filteredNotifications = useMemo(() => {
    if (filter === "unread") {
      return notifications.filter((item) => !item.is_read);
    }

    if (filter === "read") {
      return notifications.filter((item) => item.is_read);
    }

    return notifications;
  }, [filter, notifications]);

  async function refreshNotifications() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("notifications/");
      setNotifications(getNotifications(response.data));
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to refresh notifications.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  async function markAsRead(notification) {
    if (notification.is_read || busyIds.includes(notification.id)) {
      return;
    }

    setBusyIds((current) => [...current, notification.id]);
    setError("");

    try {
      await api.patch(`notifications/${notification.id}/read/`);

      setNotifications((current) =>
        current.map((item) =>
          item.id === notification.id
            ? { ...item, is_read: true }
            : item,
        ),
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to mark this notification as read.",
        ),
      );
    } finally {
      setBusyIds((current) =>
        current.filter((id) => id !== notification.id),
      );
    }
  }

  async function markAllAsRead() {
    if (unreadCount === 0 || markingAll) {
      return;
    }

    setMarkingAll(true);
    setError("");

    try {
      await api.patch("notifications/read-all/");

      setNotifications((current) =>
        current.map((item) => ({ ...item, is_read: true })),
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to mark all notifications as read.",
        ),
      );
    } finally {
      setMarkingAll(false);
    }
  }

  async function deleteNotification(notification) {
    if (deletingIds.includes(notification.id)) {
      return;
    }

    setDeletingIds((current) => [...current, notification.id]);
    setError("");

    try {
      await api.delete(`notifications/${notification.id}/`);

      setNotifications((current) =>
        current.filter((item) => item.id !== notification.id),
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to delete this notification.",
        ),
      );
    } finally {
      setDeletingIds((current) =>
        current.filter((id) => id !== notification.id),
      );
    }
  }

  return (
    <section className="notifications-page">
      <header className="notifications-page-header">
        <div>
          <p className="notifications-eyebrow">Your updates</p>
          <h1>Notifications</h1>
          <p className="notifications-description">
            Keep track of important activity and updates in ChronoTrack.
          </p>
        </div>

        <button
          type="button"
          className="notifications-secondary-button"
          onClick={refreshNotifications}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </header>

      <section className="notifications-summary">
        <div>
          <span className="notifications-summary-label">
            All notifications
          </span>
          <strong>{notifications.length}</strong>
        </div>

        <div>
          <span className="notifications-summary-label">
            Unread
          </span>
          <strong>{unreadCount}</strong>
        </div>
      </section>

      <section className="notifications-panel">
        <div className="notifications-panel-header">
          <div>
            <h2>Recent activity</h2>
            <p>Your latest account notifications.</p>
          </div>

          <button
            type="button"
            className="notifications-text-button"
            onClick={markAllAsRead}
            disabled={unreadCount === 0 || markingAll || loading}
          >
            {markingAll ? "Updating..." : "Mark all as read"}
          </button>
        </div>

        <div
          className="notifications-filters"
          aria-label="Filter notifications"
        >
          {[
            { value: "all", label: "All" },
            { value: "unread", label: "Unread" },
            { value: "read", label: "Read" },
          ].map((option) => (
            <button
              key={option.value}
              type="button"
              className={`notifications-filter ${
                filter === option.value
                  ? "notifications-filter-active"
                  : ""
              }`}
              onClick={() => setFilter(option.value)}
              aria-pressed={filter === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>

        {error && (
          <div className="notifications-error" role="alert">
            <span>{error}</span>

            <button
              type="button"
              onClick={refreshNotifications}
              disabled={loading}
            >
              Try again
            </button>
          </div>
        )}

        {loading ? (
          <div className="notifications-state">
            Loading notifications...
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="notifications-state">
            <span className="notifications-empty-mark" aria-hidden="true">
              ✓
            </span>

            <h3>
              {filter === "unread"
                ? "You're all caught up"
                : filter === "read"
                  ? "No read notifications"
                  : "No notifications yet"}
            </h3>

            <p>
              {filter === "unread"
                ? "There are no unread notifications right now."
                : filter === "read"
                  ? "Notifications you have read will appear here."
                  : "New activity and updates will appear here."}
            </p>
          </div>
        ) : (
          <div className="notifications-list">
            {filteredNotifications.map((notification) => {
              const isBusy = busyIds.includes(notification.id);
              const isDeleting = deletingIds.includes(notification.id);

              return (
                <article
                  key={notification.id}
                  className={`notification-item ${
                    notification.is_read ? "" : "notification-item-unread"
                  }`}
                >
                  <div
                    className={`notification-status ${
                      notification.is_read
                        ? "notification-status-read"
                        : "notification-status-unread"
                    }`}
                    aria-hidden="true"
                  />

                  <div className="notification-content">
                    <div className="notification-item-heading">
                      <h3>{notification.title}</h3>

                      {!notification.is_read && (
                        <span className="notification-unread-label">
                          Unread
                        </span>
                      )}
                    </div>

                    <p className="notification-message">
                      {notification.message}
                    </p>

                    <div className="notification-meta">
                      <span>
                        {getTypeLabel(notification.notification_type)}
                      </span>
                      <span aria-hidden="true">·</span>
                      <time dateTime={notification.created_at}>
                        {formatDate(notification.created_at)}
                      </time>
                    </div>

                    <div className="notification-actions">
                      {!notification.is_read && (
                        <button
                          type="button"
                          className="notifications-text-button"
                          onClick={() => markAsRead(notification)}
                          disabled={isBusy || isDeleting}
                        >
                          {isBusy ? "Updating..." : "Mark as read"}
                        </button>
                      )}

                      <button
                        type="button"
                        className="notifications-delete-button"
                        onClick={() => deleteNotification(notification)}
                        disabled={isBusy || isDeleting}
                      >
                        {isDeleting ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </section>
  );
}

export default Notifications;
