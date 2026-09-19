import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { useContext } from "react";

import { AuthContext } from "../../../context/AuthContextValue";

import api from "../../../services/api";

import "../../../styles/reports.css";


function formatHours(hours) {
  const value = Number(hours || 0);

  return `${value.toFixed(2)}h`;
}


function formatCurrency(value) {
  const amount = Number(value || 0);

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "PHP",
  }).format(amount);
}


function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleDateString(
    "en-US",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
    },
  );
}


function formatTime(value) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleTimeString(
    "en-US",
    {
      hour: "numeric",
      minute: "2-digit",
    },
  );
}


function getDayLabel(date) {
  return new Date(
    `${date}T00:00:00`,
  ).toLocaleDateString(
    "en-US",
    {
      weekday: "short",
    },
  );
}


function Reports() {
  const { user } = useContext(AuthContext);

  const [report, setReport] = useState(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const [retryCount, setRetryCount] = useState(0);


  const role = user?.role || "Employee";


  const isEmployee = role === "Employee";

  const isManager = role === "Manager";

  const isAdmin = role === "Admin";


  useEffect(() => {
    if (!user) {
      return;
    }

    let cancelled = false;


    const fetchReport = async () => {
      try {
        let endpoint = "reports/me/weekly/";


        if (isManager) {
          endpoint = "reports/team/";
        }

        if (isAdmin) {
          endpoint = "reports/organization/";
        }


        const response = await api.get(endpoint);


        if (!cancelled) {
          setReport(response.data);
          setError("");
          setLoading(false);
        }
      } catch (requestError) {
        console.error(
          "Failed to load report:",
          requestError,
        );


        if (!cancelled) {
          setError(
            requestError.response?.data?.detail ||
            "Unable to load your report.",
          );

          setLoading(false);
        }
      }
    };


    fetchReport();


    return () => {
      cancelled = true;
    };
  }, [
    user,
    isManager,
    isAdmin,
    retryCount,
  ]);


  const dailyBreakdown = useMemo(() => {
    if (!report?.entries) {
      return [];
    }


    const grouped = {};


    report.entries.forEach((entry) => {
      const date = entry.start_time
        ? entry.start_time.slice(0, 10)
        : null;


      if (!date) {
        return;
      }


      if (!grouped[date]) {
        grouped[date] = 0;
      }


      grouped[date] += Number(
        entry.duration_hours || 0,
      );
    });


    return Object.entries(grouped)
      .sort(
        ([dateA], [dateB]) =>
          new Date(dateA) -
          new Date(dateB),
      )
      .map(
        ([date, hours]) => ({
          date,
          label: getDayLabel(date),
          hours,
        }),
      );
  }, [report]);


  const maximumDailyHours = useMemo(() => {
    if (!dailyBreakdown.length) {
      return 1;
    }


    return Math.max(
      ...dailyBreakdown.map(
        (item) => item.hours,
      ),
      1,
    );
  }, [dailyBreakdown]);


  if (loading) {
    return (
      <section className="reports-page">
        <div className="reports-loading">
          Loading reports...
        </div>
      </section>
    );
  }


  if (error) {
    return (
      <section className="reports-page">

        <div className="reports-header">

          <div>
            <p className="reports-eyebrow">
              {isAdmin
                ? "Organization reports"
                : isManager
                  ? "Team reports"
                  : "Personal reports"}
            </p>

            <h1>
              {isAdmin
                ? "Organization Reports"
                : isManager
                  ? "Team Reports"
                  : "My Reports"}
            </h1>

            <p>
              {isAdmin
                ? "Review organization-wide time and productivity data."
                : isManager
                  ? "Review team time and work activity."
                  : "Review your tracked time and work activity."}
            </p>
          </div>

        </div>


        <div className="reports-error">

          <strong>
            Unable to load report
          </strong>

          <span>
            {error}
          </span>

          <button
            type="button"
            className="reports-retry-button"
            onClick={() => {
              setLoading(true);
              setReport(null);
              setError("");
              setRetryCount(
                (count) => count + 1,
              );
            }}
          >
            Try Again
          </button>

        </div>

      </section>
    );
  }


  if (!report) {
    return (
      <section className="reports-page">

        <div className="reports-header">

          <div>
            <p className="reports-eyebrow">
              {isAdmin
                ? "Organization reports"
                : isManager
                  ? "Team reports"
                  : "Personal reports"}
            </p>

            <h1>
              {isAdmin
                ? "Organization Reports"
                : isManager
                  ? "Team Reports"
                  : "My Reports"}
            </h1>

            <p>
              Review tracked time and
              work activity.
            </p>
          </div>

        </div>


        <div className="reports-empty">
          No report data is available yet.
        </div>

      </section>
    );
  }


  /*
   * ---------------------------------------------------------
   * EMPLOYEE REPORT
   * ---------------------------------------------------------
   */

  if (isEmployee) {
    const totalHours =
      Number(report.total_hours || 0);

    const billableHours =
      Number(report.billable_hours || 0);

    const nonBillableHours =
      Number(
        report.non_billable_hours || 0,
      );


    const billablePercentage =
      totalHours > 0
        ? Math.min(
            100,
            (billableHours / totalHours) *
              100,
          )
        : 0;


    const nonBillablePercentage =
      totalHours > 0
        ? Math.min(
            100,
            (nonBillableHours / totalHours) *
              100,
          )
        : 0;


    return (
      <section className="reports-page">

        <header className="reports-header">

          <div>
            <p className="reports-eyebrow">
              Personal reports
            </p>

            <h1>
              My Reports
            </h1>

            <p>
              Review your tracked time and
              work activity for the current
              week.
            </p>
          </div>


          <div className="reports-period">

            <span>
              Reporting period
            </span>

            <strong>
              {formatDate(report.week_start)}
              {" — "}
              {formatDate(report.week_end)}
            </strong>

          </div>

        </header>


        <div className="reports-summary">

          <article className="report-stat">

            <span className="report-stat-label">
              Total tracked
            </span>

            <strong className="report-stat-value">
              {formatHours(totalHours)}
            </strong>

            <span className="report-stat-meta">
              {report.total_entries || 0} completed entries
            </span>

          </article>


          <article className="report-stat">

            <span className="report-stat-label">
              Billable
            </span>

            <strong className="report-stat-value">
              {formatHours(billableHours)}
            </strong>

            <span className="report-stat-meta">
              {billablePercentage.toFixed(0)}% of tracked time
            </span>

          </article>


          <article className="report-stat">

            <span className="report-stat-label">
              Non-billable
            </span>

            <strong className="report-stat-value">
              {formatHours(nonBillableHours)}
            </strong>

            <span className="report-stat-meta">
              Internal or non-billable work
            </span>

          </article>


          <article className="report-stat">

            <span className="report-stat-label">
              Estimated earnings
            </span>

            <strong className="report-stat-value">
              {formatCurrency(
                report.total_earnings,
              )}
            </strong>

            <span className="report-stat-meta">
              From billable time
            </span>

          </article>

        </div>


        <div className="reports-grid">

          <section className="reports-panel">

            <div className="reports-panel-header">

              <div>
                <h2>
                  Weekly activity
                </h2>

                <p>
                  Hours tracked by day.
                </p>
              </div>

            </div>


            {dailyBreakdown.length === 0 ? (

              <div className="reports-panel-empty">
                No completed time entries
                for this week.
              </div>

            ) : (

              <div className="weekly-chart">

                {dailyBreakdown.map(
                  (item) => (
                    <div
                      className="weekly-chart-column"
                      key={item.date}
                    >

                      <div className="weekly-chart-value">
                        {item.hours.toFixed(1)}h
                      </div>


                      <div className="weekly-chart-track">

                        <div
                          className="weekly-chart-bar"
                          style={{
                            height: `${Math.max(
                              4,
                              (
                                item.hours /
                                maximumDailyHours
                              ) * 100,
                            )}%`,
                          }}
                        />

                      </div>


                      <span className="weekly-chart-label">
                        {item.label}
                      </span>

                    </div>
                  ),
                )}

              </div>

            )}

          </section>


          <section className="reports-panel">

            <div className="reports-panel-header">

              <div>
                <h2>
                  Time breakdown
                </h2>

                <p>
                  Billable versus
                  non-billable time.
                </p>
              </div>

            </div>


            <div className="time-breakdown">

              <div className="breakdown-row">

                <div className="breakdown-heading">

                  <span>
                    Billable
                  </span>

                  <strong>
                    {formatHours(
                      billableHours,
                    )}
                  </strong>

                </div>


                <div className="breakdown-track">

                  <div
                    className="breakdown-fill breakdown-fill-billable"
                    style={{
                      width: `${billablePercentage}%`,
                    }}
                  />

                </div>

              </div>


              <div className="breakdown-row">

                <div className="breakdown-heading">

                  <span>
                    Non-billable
                  </span>

                  <strong>
                    {formatHours(
                      nonBillableHours,
                    )}
                  </strong>

                </div>


                <div className="breakdown-track">

                  <div
                    className="breakdown-fill breakdown-fill-non-billable"
                    style={{
                      width: `${nonBillablePercentage}%`,
                    }}
                  />

                </div>

              </div>

            </div>

          </section>

        </div>


        <section className="reports-panel reports-entries-panel">

          <div className="reports-panel-header">

            <div>
              <h2>
                Time entries
              </h2>

              <p>
                Completed work recorded
                during this reporting period.
              </p>
            </div>


            <span className="reports-entry-count">
              {report.entries?.length || 0} entries
            </span>

          </div>


          {report.entries?.length ? (

            <div className="reports-table-wrapper">

              <table className="reports-table">

                <thead>

                  <tr>
                    <th>Date</th>
                    <th>Project</th>
                    <th>Task</th>
                    <th>Time</th>
                    <th>Duration</th>
                    <th>Type</th>
                    <th>Earnings</th>
                  </tr>

                </thead>


                <tbody>

                  {report.entries.map(
                    (entry) => (
                      <tr key={entry.id}>

                        <td>
                          {formatDate(
                            entry.start_time,
                          )}
                        </td>


                        <td>
                          <strong>
                            {entry.project || "—"}
                          </strong>
                        </td>


                        <td>
                          {entry.task || "No task"}
                        </td>


                        <td>
                          <span className="reports-time-range">
                            {formatTime(
                              entry.start_time,
                            )}
                            {" — "}
                            {formatTime(
                              entry.end_time,
                            )}
                          </span>
                        </td>


                        <td>
                          <strong>
                            {formatHours(
                              entry.duration_hours,
                            )}
                          </strong>
                        </td>


                        <td>
                          <span
                            className={
                              entry.billable
                                ? "report-badge report-badge-billable"
                                : "report-badge report-badge-neutral"
                            }
                          >
                            {entry.billable
                              ? "Billable"
                              : "Non-billable"}
                          </span>
                        </td>


                        <td>
                          {formatCurrency(
                            entry.earnings,
                          )}
                        </td>

                      </tr>
                    ),
                  )}

                </tbody>

              </table>

            </div>

          ) : (

            <div className="reports-panel-empty">
              No completed time entries
              for this week.
            </div>

          )}

        </section>

      </section>
    );
  }


  /*
   * ---------------------------------------------------------
   * MANAGER / ADMIN REPORT
   * ---------------------------------------------------------
   */

  const totalHours =
    Number(report.total_hours || 0);

  const billableHours =
    Number(report.billable_hours || 0);

  const nonBillableHours =
    Number(report.non_billable_hours || 0);


  const reportTitle = isAdmin
    ? "Organization Reports"
    : "Team Reports";

  const reportEyebrow = isAdmin
    ? "Organization reports"
    : "Team reports";


  return (
    <section className="reports-page">

      <header className="reports-header">

        <div>
          <p className="reports-eyebrow">
            {reportEyebrow}
          </p>

          <h1>
            {reportTitle}
          </h1>

          <p>
            {isAdmin
              ? "Review organization-wide time and work activity."
              : "Review team time and work activity."}
          </p>
        </div>

      </header>


      <div className="reports-summary">

        <article className="report-stat">

          <span className="report-stat-label">
            Total tracked
          </span>

          <strong className="report-stat-value">
            {formatHours(totalHours)}
          </strong>

          <span className="report-stat-meta">
            {report.total_entries || 0} completed entries
          </span>

        </article>


        <article className="report-stat">

          <span className="report-stat-label">
            Billable
          </span>

          <strong className="report-stat-value">
            {formatHours(billableHours)}
          </strong>

          <span className="report-stat-meta">
            Billable team time
          </span>

        </article>


        <article className="report-stat">

          <span className="report-stat-label">
            Non-billable
          </span>

          <strong className="report-stat-value">
            {formatHours(nonBillableHours)}
          </strong>

          <span className="report-stat-meta">
            Internal or non-billable work
          </span>

        </article>


        <article className="report-stat">

          <span className="report-stat-label">
            Estimated earnings
          </span>

          <strong className="report-stat-value">
            {formatCurrency(
              report.estimated_earnings,
            )}
          </strong>

          <span className="report-stat-meta">
            From billable time
          </span>

        </article>

      </div>


      <div className="reports-grid">

        <section className="reports-panel">

          <div className="reports-panel-header">

            <div>
              <h2>
                {isAdmin
                  ? "Projects"
                  : "Team projects"}
              </h2>

              <p>
                {isAdmin
                  ? "Tracked time across organization projects."
                  : "Tracked time across your projects."}
              </p>
            </div>

          </div>


          {report.projects?.length ? (

            <div className="reports-table-wrapper">

              <table className="reports-table">

                <thead>

                  <tr>
                    <th>Project</th>

                    {isAdmin && (
                      <th>Owner</th>
                    )}

                    <th>Client</th>
                    <th>Status</th>
                    <th>Hours</th>
                    <th>Billable</th>
                    <th>Earnings</th>
                  </tr>

                </thead>


                <tbody>

                  {report.projects.map(
                    (project) => (
                      <tr key={project.id}>

                        <td>
                          <strong>
                            {project.name}
                          </strong>
                        </td>


                        {isAdmin && (
                          <td>
                            {project.owner?.username ||
                              "—"}
                          </td>
                        )}


                        <td>
                          {project.client || "—"}
                        </td>


                        <td>
                          {project.status || "—"}
                        </td>


                        <td>
                          {formatHours(
                            project.total_hours,
                          )}
                        </td>


                        <td>
                          {formatHours(
                            project.billable_hours,
                          )}
                        </td>


                        <td>
                          {formatCurrency(
                            project.estimated_earnings,
                          )}
                        </td>

                      </tr>
                    ),
                  )}

                </tbody>

              </table>

            </div>

          ) : (

            <div className="reports-panel-empty">
              No project report data available.
            </div>

          )}

        </section>


        <section className="reports-panel">

          <div className="reports-panel-header">

            <div>
              <h2>
                {isAdmin
                  ? "Organization members"
                  : "Team members"}
              </h2>

              <p>
                Tracked time by member.
              </p>
            </div>

          </div>


          {report.team_members?.length ? (

            <div className="reports-table-wrapper">

              <table className="reports-table">

                <thead>

                  <tr>
                    <th>Member</th>
                    <th>Entries</th>
                    <th>Hours</th>
                    <th>Billable</th>
                    <th>Earnings</th>
                  </tr>

                </thead>


                <tbody>

                  {report.team_members.map(
                    (member) => (
                      <tr key={member.id}>

                        <td>
                          <strong>
                            {member.first_name ||
                              member.last_name
                              ? `${member.first_name} ${member.last_name}`.trim()
                              : member.username}
                          </strong>
                        </td>


                        <td>
                          {member.total_entries || 0}
                        </td>


                        <td>
                          {formatHours(
                            member.total_hours,
                          )}
                        </td>


                        <td>
                          {formatHours(
                            member.billable_hours,
                          )}
                        </td>


                        <td>
                          {formatCurrency(
                            member.estimated_earnings,
                          )}
                        </td>

                      </tr>
                    ),
                  )}

                </tbody>

              </table>

            </div>

          ) : (

            <div className="reports-panel-empty">
              No member report data available.
            </div>

          )}

        </section>

      </div>


      <section className="reports-panel reports-entries-panel">

        <div className="reports-panel-header">

          <div>
            <h2>
              Recent time entries
            </h2>

            <p>
              Recently completed work recorded
              by the {isAdmin ? "organization" : "team"}.
            </p>
          </div>


          <span className="reports-entry-count">
            {report.recent_entries?.length || 0} entries
          </span>

        </div>


        {report.recent_entries?.length ? (

          <div className="reports-table-wrapper">

            <table className="reports-table">

              <thead>

                <tr>

                  {isAdmin && (
                    <th>Member</th>
                  )}

                  <th>Date</th>
                  <th>Project</th>
                  <th>Task</th>
                  <th>Duration</th>
                  <th>Type</th>
                  <th>Earnings</th>

                </tr>

              </thead>


              <tbody>

                {report.recent_entries.map(
                  (entry) => (
                    <tr key={entry.id}>

                      {isAdmin && (
                        <td>
                          <strong>
                            {entry.owner?.username ||
                              "—"}
                          </strong>
                        </td>
                      )}


                      <td>
                        {formatDate(
                          entry.start_time,
                        )}
                      </td>


                      <td>
                        <strong>
                          {entry.project || "—"}
                        </strong>
                      </td>


                      <td>
                        {entry.task || "No task"}
                      </td>


                      <td>
                        {formatHours(
                          entry.duration_hours,
                        )}
                      </td>


                      <td>
                        <span
                          className={
                            entry.billable
                              ? "report-badge report-badge-billable"
                              : "report-badge report-badge-neutral"
                          }
                        >
                          {entry.billable
                            ? "Billable"
                            : "Non-billable"}
                        </span>
                      </td>


                      <td>
                        {formatCurrency(
                          entry.earnings,
                        )}
                      </td>

                    </tr>
                  ),
                )}

              </tbody>

            </table>

          </div>

        ) : (

          <div className="reports-panel-empty">
            No recent completed entries available.
          </div>

        )}

      </section>

    </section>
  );
}


export default Reports;