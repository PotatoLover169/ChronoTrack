import {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { AuthContext } from "../../../context/AuthContextValue";
import api from "../../../services/api";
import "../../../styles/leave.css";

/* =========================
   HELPERS
========================= */

function getList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function getErrorMessage(error, fallback) {
  const data = error?.response?.data;

  if (typeof data?.detail === "string") return data.detail;
  if (typeof data?.message === "string") return data.message;

  if (data && typeof data === "object") {
    for (const value of Object.values(data)) {
      if (typeof value === "string") return value;

      if (Array.isArray(value) && value.length > 0) {
        return String(value[0]);
      }
    }
  }

  return fallback;
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(`${value}T00:00:00`);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDateTime(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "—";

  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatDays(value) {
  const days = Number(value || 0);

  return `${days.toLocaleString("en-US", {
    maximumFractionDigits: 2,
  })} ${days === 1 ? "day" : "days"}`;
}

function getEmployeeName(employee) {
  if (typeof employee === "object" && employee !== null) {
    const name = [
      employee.first_name,
      employee.last_name,
    ]
      .filter(Boolean)
      .join(" ");

    return (
      name ||
      employee.username ||
      `Employee #${employee.id ?? "—"}`
    );
  }

  return employee ? `Employee #${employee}` : "Employee";
}

function getStatusLabel(status) {
  const labels = {
    pending: "Pending",
    approved: "Approved",
    rejected: "Rejected",
    cancelled: "Cancelled",
  };

  return labels[status] || status || "Unknown";
}

function StatusBadge({ status }) {
  return (
    <span className={`leave-status leave-status-${status || "unknown"}`}>
      <span className="leave-status-dot" />
      {getStatusLabel(status)}
    </span>
  );
}

/* =========================
   LEAVE PAGE
========================= */

function Leave() {
  const { user } = useContext(AuthContext);

  const role = user?.role || "Employee";
  const isEmployee = role === "Employee";
  const isManagerOrAdmin =
    role === "Manager" || role === "Admin";

  /* =========================
     STATE
  ========================= */

  const [leaveTypes, setLeaveTypes] = useState([]);
  const [balances, setBalances] = useState([]);
  const [requests, setRequests] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [processingId, setProcessingId] = useState(null);
  const [savingBalanceId, setSavingBalanceId] = useState(null);

  const [form, setForm] = useState({
    leave_type: "",
    start_date: "",
    end_date: "",
    reason: "",
  });

  const [reviewComments, setReviewComments] = useState({});
  const [balanceDrafts, setBalanceDrafts] = useState({});

  const currentYear = new Date().getFullYear();

  /* =========================
     REUSABLE DATA LOADER
  ========================= */

  const loadLeaveData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const typePromise = api.get("leave/types/");

      const [
        typesResponse,
        balancesResponse,
        requestsResponse,
      ] = await Promise.all([
        typePromise,
        isEmployee
          ? api.get("leave/balances/")
          : api.get("leave/balances/manage/"),
        isEmployee
          ? api.get("leave/requests/my/")
          : api.get("leave/requests/"),
      ]);

      setLeaveTypes(getList(typesResponse.data));
      setBalances(getList(balancesResponse.data));
      setRequests(getList(requestsResponse.data));
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "We couldn't load Leave. Please try again."
        )
      );
    } finally {
      setLoading(false);
    }
  }, [isEmployee]);

  /* =========================
     INITIAL DATA LOADING
  ========================= */

  useEffect(() => {
    if (!user) return undefined;

    let cancelled = false;

    async function fetchInitialData() {
      try {
        const typePromise = api.get("leave/types/");

        const [
          typesResponse,
          balancesResponse,
          requestsResponse,
        ] = await Promise.all([
          typePromise,
          isEmployee
            ? api.get("leave/balances/")
            : api.get("leave/balances/manage/"),
          isEmployee
            ? api.get("leave/requests/my/")
            : api.get("leave/requests/"),
        ]);

        if (cancelled) return;

        setLeaveTypes(getList(typesResponse.data));
        setBalances(getList(balancesResponse.data));
        setRequests(getList(requestsResponse.data));
        setError("");
      } catch (requestError) {
        if (!cancelled) {
          setError(
            getErrorMessage(
              requestError,
              "We couldn't load Leave. Please try again."
            )
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchInitialData();

    return () => {
      cancelled = true;
    };
  }, [user, isEmployee]);

  /* =========================
     DERIVED DATA
  ========================= */

  const employeeBalances = useMemo(
    () =>
      balances.filter(
        (balance) => Number(balance.year) === currentYear
      ),
    [balances, currentYear]
  );

  const totalAllocated = useMemo(
    () =>
      employeeBalances.reduce(
        (total, balance) =>
          total + Number(balance.allocated_days || 0),
        0
      ),
    [employeeBalances]
  );

  const totalUsed = useMemo(
    () =>
      employeeBalances.reduce(
        (total, balance) =>
          total + Number(balance.used_days || 0),
        0
      ),
    [employeeBalances]
  );

  const totalRemaining = useMemo(
    () =>
      employeeBalances.reduce(
        (total, balance) =>
          total + Number(balance.remaining_days || 0),
        0
      ),
    [employeeBalances]
  );

  const pendingCount = requests.filter(
    (request) => request.status === "pending"
  ).length;

  const selectedBalance = useMemo(() => {
    if (!form.leave_type || !form.start_date) return null;

    const year = Number(form.start_date.slice(0, 4));

    return (
      balances.find(
        (balance) =>
          String(balance.leave_type?.id) ===
            String(form.leave_type) &&
          Number(balance.year) === year
      ) || null
    );
  }, [balances, form.leave_type, form.start_date]);

  /* =========================
     FORM HANDLERS
  ========================= */

  const updateForm = (event) => {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  /* =========================
     SUBMIT REQUEST
  ========================= */

  const handleCreateRequest = async (event) => {
    event.preventDefault();

    setError("");
    setNotice("");

    if (
      !form.leave_type ||
      !form.start_date ||
      !form.end_date ||
      !form.reason.trim()
    ) {
      setError("Complete all fields before submitting your request.");
      return;
    }

    if (form.end_date < form.start_date) {
      setError("The end date cannot be earlier than the start date.");
      return;
    }

    if (
      form.start_date.slice(0, 4) !==
      form.end_date.slice(0, 4)
    ) {
      setError("Leave requests must be within one calendar year.");
      return;
    }

    if (
      !selectedBalance ||
      Number(selectedBalance.remaining_days || 0) <= 0
    ) {
      setError(
        "There is no available balance for this leave type and year. Please contact your manager."
      );
      return;
    }

    setSubmitting(true);

    try {
      await api.post("leave/requests/create/", {
        leave_type: Number(form.leave_type),
        start_date: form.start_date,
        end_date: form.end_date,
        reason: form.reason.trim(),
      });

      setForm({
        leave_type: "",
        start_date: "",
        end_date: "",
        reason: "",
      });

      setNotice("Your leave request has been submitted.");

      await loadLeaveData();
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Your request could not be submitted."
        )
      );
    } finally {
      setSubmitting(false);
    }
  };

  /* =========================
     CANCEL REQUEST
  ========================= */

  const handleCancelRequest = async (requestId) => {
    if (
      !window.confirm("Cancel this pending leave request?")
    ) {
      return;
    }

    setProcessingId(requestId);
    setError("");
    setNotice("");

    try {
      await api.patch(
        `leave/requests/${requestId}/cancel/`
      );

      setNotice("The leave request was cancelled.");

      await loadLeaveData();
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "The leave request could not be cancelled."
        )
      );
    } finally {
      setProcessingId(null);
    }
  };

  /* =========================
     APPROVE / REJECT REQUEST
  ========================= */

  const handleReviewRequest = async (requestId, action) => {
    const comment = (
      reviewComments[requestId] || ""
    ).trim();

    if (action === "reject" && !comment) {
      setError("Add a comment before rejecting a leave request.");
      return;
    }

    const actionLabel =
      action === "approve" ? "approve" : "reject";

    if (
      !window.confirm(
        `Are you sure you want to ${actionLabel} this leave request?`
      )
    ) {
      return;
    }

    setProcessingId(requestId);
    setError("");
    setNotice("");

    try {
      await api.patch(
        `leave/requests/${requestId}/${action}/`,
        { manager_comment: comment }
      );

      setNotice(
        action === "approve"
          ? "Leave request approved."
          : "Leave request rejected."
      );

      setReviewComments((current) => ({
        ...current,
        [requestId]: "",
      }));

      await loadLeaveData();
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          `The request could not be ${actionLabel}d.`
        )
      );
    } finally {
      setProcessingId(null);
    }
  };

  /* =========================
     SAVE LEAVE ALLOCATION
  ========================= */

  const handleSaveBalance = async (balance) => {
    const value = balanceDrafts[balance.id];

    if (value === undefined || value === "") {
      setError("Enter the allocated leave days before saving.");
      return;
    }

    const allocatedDays = Number(value);

    if (
      !Number.isFinite(allocatedDays) ||
      allocatedDays < 0
    ) {
      setError(
        "Allocated leave days must be a valid non-negative number."
      );
      return;
    }

    if (
      allocatedDays < Number(balance.used_days || 0)
    ) {
      setError(
        "Allocated leave days cannot be less than days already used."
      );
      return;
    }

    setSavingBalanceId(balance.id);
    setError("");
    setNotice("");

    try {
      await api.patch(
        `leave/balances/manage/${balance.id}/`,
        {
          allocated_days: allocatedDays.toFixed(2),
        }
      );

      setNotice(`Leave balance #${balance.id} was updated.`);

      setBalanceDrafts((current) => {
        const next = { ...current };
        delete next[balance.id];
        return next;
      });

      await loadLeaveData();
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "The leave balance could not be updated."
        )
      );
    } finally {
      setSavingBalanceId(null);
    }
  };

  /* =========================
     LOADING STATE
  ========================= */

  if (loading && user) {
    return (
      <section className="leave-page">
        <div className="leave-loading">
          <span className="leave-spinner" />
          <p>Loading leave information…</p>
        </div>
      </section>
    );
  }

  /* =========================
     PAGE
  ========================= */

  return (
    <section className="leave-page">
      <header className="leave-header">
        <div>
          <p className="leave-eyebrow">
            {isEmployee ? "Personal time off" : "People operations"}
          </p>

          <h1>
            {isEmployee ? "Leave" : "Leave management"}
          </h1>

          <p className="leave-header-description">
            {isEmployee
              ? "Check your available leave, submit a request, and track its status."
              : "Review pending leave requests and maintain annual leave allocations."}
          </p>
        </div>

        <button
          type="button"
          className="leave-secondary-button"
          onClick={loadLeaveData}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </header>

      {error && (
        <div
          className="leave-alert leave-alert-error"
          role="alert"
        >
          <span>{error}</span>

          <button
            type="button"
            onClick={() => setError("")}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {notice && (
        <div
          className="leave-alert leave-alert-success"
          role="status"
        >
          <span>{notice}</span>

          <button
            type="button"
            onClick={() => setNotice("")}
            aria-label="Dismiss message"
          >
            ×
          </button>
        </div>
      )}

      {/* =========================
          EMPLOYEE VIEW
      ========================= */}

      {isEmployee ? (
        <>
          <div className="leave-summary-grid">
            <article className="leave-summary-card">
              <span className="leave-summary-label">
                Allocated this year
              </span>
              <strong>{formatDays(totalAllocated)}</strong>
              <span className="leave-summary-footnote">
                {currentYear} allocation
              </span>
            </article>

            <article className="leave-summary-card">
              <span className="leave-summary-label">Used</span>
              <strong>{formatDays(totalUsed)}</strong>
              <span className="leave-summary-footnote">
                Approved leave
              </span>
            </article>

            <article className="leave-summary-card leave-summary-card-accent">
              <span className="leave-summary-label">
                Remaining
              </span>
              <strong>{formatDays(totalRemaining)}</strong>
              <span className="leave-summary-footnote">
                Across current-year balances
              </span>
            </article>

            <article className="leave-summary-card">
              <span className="leave-summary-label">
                Pending requests
              </span>
              <strong>{pendingCount}</strong>
              <span className="leave-summary-footnote">
                Awaiting review
              </span>
            </article>
          </div>

          <div className="leave-content-grid">
            {/* Request form */}

            <section className="leave-panel leave-request-panel">
              <div className="leave-panel-heading">
                <div>
                  <h2>Request leave</h2>
                  <p>
                    Submit your dates and a short reason.
                  </p>
                </div>
              </div>

              {leaveTypes.length === 0 ? (
                <div className="leave-inline-empty">
                  No leave types are currently available.
                  Please contact your manager.
                </div>
              ) : (
                <form
                  className="leave-form"
                  onSubmit={handleCreateRequest}
                >
                  <label className="leave-field leave-field-full">
                    <span>Leave type</span>

                    <select
                      name="leave_type"
                      value={form.leave_type}
                      onChange={updateForm}
                      required
                    >
                      <option value="">
                        Select leave type
                      </option>

                      {leaveTypes.map((type) => (
                        <option
                          key={type.id}
                          value={type.id}
                        >
                          {type.name}
                          {type.is_paid ? " · Paid" : " · Unpaid"}
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="leave-form-row">
                    <label className="leave-field">
                      <span>Start date</span>

                      <input
                        type="date"
                        name="start_date"
                        value={form.start_date}
                        onChange={updateForm}
                        required
                      />
                    </label>

                    <label className="leave-field">
                      <span>End date</span>

                      <input
                        type="date"
                        name="end_date"
                        value={form.end_date}
                        min={form.start_date || undefined}
                        onChange={updateForm}
                        required
                      />
                    </label>
                  </div>

                  {form.leave_type && form.start_date && (
                    <div className="leave-balance-hint">
                      {selectedBalance ? (
                        <>
                          <span>
                            Available for {form.start_date.slice(0, 4)}
                          </span>
                          <strong>
                            {formatDays(
                              selectedBalance.remaining_days
                            )}
                          </strong>
                        </>
                      ) : (
                        <span>
                          No allocated balance was found for this
                          leave type in {form.start_date.slice(0, 4)}.
                        </span>
                      )}
                    </div>
                  )}

                  <label className="leave-field leave-field-full">
                    <span>Reason</span>

                    <textarea
                      name="reason"
                      value={form.reason}
                      onChange={updateForm}
                      rows={4}
                      maxLength={2000}
                      placeholder="Briefly explain your request…"
                      required
                    />
                  </label>

                  <button
                    type="submit"
                    className="leave-primary-button"
                    disabled={submitting}
                  >
                    {submitting ? "Submitting…" : "Submit request"}
                  </button>
                </form>
              )}
            </section>

            {/* Leave balances */}

            <section className="leave-panel">
              <div className="leave-panel-heading">
                <div>
                  <h2>Leave balances</h2>
                  <p>
                    Your allocated, used, and remaining days.
                  </p>
                </div>
              </div>

              {employeeBalances.length === 0 ? (
                <div className="leave-inline-empty">
                  No leave balances have been allocated for{" "}
                  {currentYear}.
                </div>
              ) : (
                <div className="leave-balance-list">
                  {employeeBalances.map((balance) => {
                    const allocated = Number(
                      balance.allocated_days || 0
                    );
                    const used = Number(balance.used_days || 0);
                    const remaining = Number(
                      balance.remaining_days || 0
                    );

                    const usedPercentage =
                      allocated > 0
                        ? Math.min(
                            100,
                            Math.max(0, (used / allocated) * 100)
                          )
                        : 0;

                    return (
                      <article
                        className="leave-balance-item"
                        key={balance.id}
                      >
                        <div className="leave-balance-top">
                          <div>
                            <strong>
                              {balance.leave_type?.name || "Leave"}
                            </strong>
                            <span>
                              {balance.leave_type?.is_paid
                                ? "Paid leave"
                                : "Unpaid leave"}
                            </span>
                          </div>

                          <strong className="leave-balance-remaining">
                            {formatDays(remaining)}
                          </strong>
                        </div>

                        <div className="leave-progress-track">
                          <span
                            className="leave-progress-fill"
                            style={{
                              width: `${usedPercentage}%`,
                            }}
                          />
                        </div>

                        <div className="leave-balance-meta">
                          <span>{formatDays(used)} used</span>
                          <span>
                            {formatDays(allocated)} allocated
                          </span>
                        </div>
                      </article>
                    );
                  })}
                </div>
              )}
            </section>
          </div>

          {/* My requests */}

          <section className="leave-panel leave-history-panel">
            <div className="leave-panel-heading leave-history-heading">
              <div>
                <h2>My requests</h2>
                <p>
                  Track the status of your submitted leave requests.
                </p>
              </div>

              <span className="leave-count-pill">
                {requests.length} total
              </span>
            </div>

            {requests.length === 0 ? (
              <div className="leave-empty-state">
                <div className="leave-empty-mark">—</div>
                <h3>No leave requests yet</h3>
                <p>
                  Your submitted requests will appear here.
                </p>
              </div>
            ) : (
              <div className="leave-table-wrap">
                <table className="leave-table">
                  <thead>
                    <tr>
                      <th>Leave type</th>
                      <th>Dates</th>
                      <th>Days</th>
                      <th>Submitted</th>
                      <th>Status</th>
                      <th>Review comment</th>
                      <th>
                        <span className="leave-sr-only">
                          Actions
                        </span>
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {requests.map((request) => (
                      <tr key={request.id}>
                        <td>
                          <strong>
                            {request.leave_type?.name || "Leave"}
                          </strong>
                          <span className="leave-table-subtext">
                            Request #{request.id}
                          </span>
                        </td>

                        <td>
                          <span>
                            {formatDate(request.start_date)}
                          </span>
                          <span className="leave-table-subtext">
                            to {formatDate(request.end_date)}
                          </span>
                        </td>

                        <td>{formatDays(request.days)}</td>

                        <td>
                          {formatDateTime(request.requested_at)}
                        </td>

                        <td>
                          <StatusBadge status={request.status} />
                        </td>

                        <td className="leave-comment-cell">
                          {request.manager_comment || "—"}
                        </td>

                        <td>
                          {request.status === "pending" && (
                            <button
                              type="button"
                              className="leave-text-button leave-danger-text"
                              disabled={processingId === request.id}
                              onClick={() =>
                                handleCancelRequest(request.id)
                              }
                            >
                              {processingId === request.id
                                ? "Cancelling…"
                                : "Cancel"}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      ) : (
        /* =========================
           MANAGER / ADMIN VIEW
        ========================= */

        <>
          <div className="leave-summary-grid leave-summary-grid-manager">
            <article className="leave-summary-card">
              <span className="leave-summary-label">
                Pending requests
              </span>
              <strong>{pendingCount}</strong>
              <span className="leave-summary-footnote">
                Require a decision
              </span>
            </article>

            <article className="leave-summary-card">
              <span className="leave-summary-label">
                Balances listed
              </span>
              <strong>{balances.length}</strong>
              <span className="leave-summary-footnote">
                Employee allocations
              </span>
            </article>

            <article className="leave-summary-card">
              <span className="leave-summary-label">
                Leave types
              </span>
              <strong>{leaveTypes.length}</strong>
              <span className="leave-summary-footnote">
                Currently available
              </span>
            </article>
          </div>

          {/* Requests awaiting review */}

          <section className="leave-panel leave-history-panel">
            <div className="leave-panel-heading leave-history-heading">
              <div>
                <h2>Requests awaiting review</h2>
                <p>
                  Only pending requests are returned by this
                  review endpoint.
                </p>
              </div>

              <span className="leave-count-pill">
                {pendingCount} pending
              </span>
            </div>

            {requests.length === 0 ? (
              <div className="leave-empty-state">
                <div className="leave-empty-mark">✓</div>
                <h3>All caught up</h3>
                <p>
                  There are no pending leave requests to review.
                </p>
              </div>
            ) : (
              <div className="leave-review-list">
                {requests.map((request) => (
                  <article
                    className="leave-review-card"
                    key={request.id}
                  >
                    <div className="leave-review-main">
                      <div className="leave-review-title-row">
                        <div>
                          <p className="leave-review-kicker">
                            Request #{request.id}
                          </p>
                          <h3>
                            {getEmployeeName(request.employee)}
                          </h3>
                        </div>

                        <StatusBadge status={request.status} />
                      </div>

                      <div className="leave-review-details">
                        <div>
                          <span>Leave type</span>
                          <strong>
                            {request.leave_type?.name || "Leave"}
                          </strong>
                        </div>

                        <div>
                          <span>Requested dates</span>
                          <strong>
                            {formatDate(request.start_date)} –{" "}
                            {formatDate(request.end_date)}
                          </strong>
                        </div>

                        <div>
                          <span>Duration</span>
                          <strong>{formatDays(request.days)}</strong>
                        </div>

                        <div>
                          <span>Submitted</span>
                          <strong>
                            {formatDateTime(request.requested_at)}
                          </strong>
                        </div>
                      </div>

                      <div className="leave-review-reason">
                        <span>Reason provided</span>
                        <p>
                          {request.reason || "No reason provided."}
                        </p>
                      </div>

                      {request.status === "pending" && (
                        <div className="leave-review-actions">
                          <label className="leave-field leave-review-comment">
                            <span>
                              Review comment{" "}
                              <small>
                                (required for rejection)
                              </small>
                            </span>

                            <textarea
                              value={
                                reviewComments[request.id] || ""
                              }
                              onChange={(event) =>
                                setReviewComments((current) => ({
                                  ...current,
                                  [request.id]: event.target.value,
                                }))
                              }
                              rows={2}
                              maxLength={2000}
                              placeholder="Add an optional approval note or a reason for rejection…"
                            />
                          </label>

                          <div className="leave-review-buttons">
                            <button
                              type="button"
                              className="leave-secondary-button"
                              disabled={processingId === request.id}
                              onClick={() =>
                                handleReviewRequest(
                                  request.id,
                                  "reject"
                                )
                              }
                            >
                              {processingId === request.id
                                ? "Saving…"
                                : "Reject"}
                            </button>

                            <button
                              type="button"
                              className="leave-primary-button"
                              disabled={processingId === request.id}
                              onClick={() =>
                                handleReviewRequest(
                                  request.id,
                                  "approve"
                                )
                              }
                            >
                              {processingId === request.id
                                ? "Saving…"
                                : "Approve request"}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          {/* Leave balance allocations */}

          <section className="leave-panel leave-history-panel">
            <div className="leave-panel-heading leave-history-heading">
              <div>
                <h2>Leave balance allocations</h2>
                <p>
                  Adjust allocated days without changing days
                  already used.
                </p>
              </div>

              <span className="leave-count-pill">
                {balances.length} balances
              </span>
            </div>

            {balances.length === 0 ? (
              <div className="leave-inline-empty">
                No employee leave balances are available to manage.
              </div>
            ) : (
              <div className="leave-table-wrap">
                <table className="leave-table">
                  <thead>
                    <tr>
                      <th>Employee</th>
                      <th>Leave type</th>
                      <th>Year</th>
                      <th>Used</th>
                      <th>Remaining</th>
                      <th>Allocated days</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {balances.map((balance) => (
                      <tr key={balance.id}>
                        <td>
                          {getEmployeeName(balance.employee)}
                        </td>

                        <td>
                          {balance.leave_type?.name || "Leave"}
                        </td>

                        <td>{balance.year}</td>

                        <td>{formatDays(balance.used_days)}</td>

                        <td>
                          {formatDays(balance.remaining_days)}
                        </td>

                        <td>
                          <input
                            className="leave-allocation-input"
                            type="number"
                            min={balance.used_days || 0}
                            step="0.25"
                            aria-label={`Allocated leave days for balance ${balance.id}`}
                            value={
                              balanceDrafts[balance.id] ??
                              balance.allocated_days ??
                              ""
                            }
                            onChange={(event) =>
                              setBalanceDrafts((current) => ({
                                ...current,
                                [balance.id]: event.target.value,
                              }))
                            }
                          />
                        </td>

                        <td>
                          <button
                            type="button"
                            className="leave-text-button"
                            disabled={
                              savingBalanceId === balance.id
                            }
                            onClick={() =>
                              handleSaveBalance(balance)
                            }
                          >
                            {savingBalanceId === balance.id
                              ? "Saving…"
                              : "Save"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}

      <p className="leave-footer-note">
        Leave balances are updated by the system when a request
        is approved.
        {isManagerOrAdmin
          ? " Review actions are restricted by the backend to authorized managers and admins."
          : " If your allocation is missing or incorrect, contact your manager."}
      </p>
    </section>
  );
}

export default Leave;