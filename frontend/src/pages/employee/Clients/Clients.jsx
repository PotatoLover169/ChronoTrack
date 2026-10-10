import { useEffect, useMemo, useState } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import "../../../styles/clients.css";

const EMPTY_FORM = {
  name: "",
  company: "",
  email: "",
  phone: "",
  notes: "",
};

function getErrorMessage(error, fallback) {
  const data = error?.response?.data;

  if (typeof data?.detail === "string") return data.detail;

  if (data && typeof data === "object") {
    for (const value of Object.values(data)) {
      if (Array.isArray(value) && value.length) return String(value[0]);
      if (typeof value === "string") return value;
    }
  }

  return fallback;
}

function formatHours(value) {
  return `${Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  })} h`;
}

function Clients() {
  const { user } = useAuth();
  const canManageClients =
    user?.role === "Manager" || user?.role === "Admin";

  const [clients, setClients] = useState([]);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [statisticsLoading, setStatisticsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadClients() {
      try {
        const response = await api.get("clients/");
        const data = response.data;

        if (!cancelled) {
          setClients(Array.isArray(data) ? data : data?.results ?? []);
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(
            getErrorMessage(
              requestError,
              "Unable to load clients. Please try again."
            )
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadClients();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredClients = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return clients;

    return clients.filter((client) =>
      [client.name, client.company, client.email, client.phone].some(
        (value) => String(value || "").toLowerCase().includes(query)
      )
    );
  }, [clients, search]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  function resetForm() {
    setForm(EMPTY_FORM);
    setEditingId(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!canManageClients || saving) return;

    setSaving(true);
    setError("");
    setSuccess("");

    const payload = {
      name: form.name.trim(),
      company: form.company.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      notes: form.notes.trim(),
    };

    try {
      if (editingId !== null) {
        const response = await api.patch(`clients/${editingId}/`, payload);

        setClients((current) =>
          current.map((client) =>
            client.id === editingId ? response.data : client
          )
        );

        setSuccess("Client updated successfully.");
      } else {
        const response = await api.post("clients/", payload);

        setClients((current) =>
          [...current, response.data].sort((a, b) =>
            String(a.name).localeCompare(String(b.name))
          )
        );

        setSuccess("Client created successfully.");
      }

      resetForm();
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to save the client. Check the required fields and permissions."
        )
      );
    } finally {
      setSaving(false);
    }
  }

  function handleEdit(client) {
    if (!canManageClients) return;

    setForm({
      name: client.name || "",
      company: client.company || "",
      email: client.email || "",
      phone: client.phone || "",
      notes: client.notes || "",
    });

    setEditingId(client.id);
    setError("");
    setSuccess("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleDelete(client) {
    if (!canManageClients) return;

    const confirmed = window.confirm(
      `Delete "${client.name}"? This action cannot be undone.`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      await api.delete(`clients/${client.id}/`);

      setClients((current) =>
        current.filter((item) => item.id !== client.id)
      );

      if (editingId === client.id) resetForm();

      if (selectedId === client.id) {
        setSelectedId(null);
        setStatistics(null);
      }

      setSuccess("Client deleted successfully.");
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to delete this client. It may still be linked to projects."
        )
      );
    }
  }

  async function handleViewStatistics(client) {
    if (selectedId === client.id) {
      setSelectedId(null);
      setStatistics(null);
      return;
    }

    setSelectedId(client.id);
    setStatistics(null);
    setStatisticsLoading(true);
    setError("");

    try {
      const response = await api.get(
        `clients/${client.id}/dashboard/`
      );
      setStatistics(response.data);
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to load client statistics."
        )
      );
      setSelectedId(null);
    } finally {
      setStatisticsLoading(false);
    }
  }

  return (
    <section className="clients-page">
      <header className="clients-header">
        <div>
          <p className="clients-eyebrow">WORKSPACE</p>
          <h1>Clients</h1>
          <p>
            {canManageClients
              ? "Manage client records and review their project activity."
              : "View clients connected to your assigned projects."}
          </p>
        </div>

        <div className="clients-total">
          <span>Accessible clients</span>
          <strong>{clients.length}</strong>
        </div>
      </header>

      {error && (
        <div className="clients-message clients-message-error" role="alert">
          <span>{error}</span>
          <button type="button" onClick={() => setError("")}>
            Dismiss
          </button>
        </div>
      )}

      {success && (
        <div className="clients-message clients-message-success" role="status">
          <span>{success}</span>
          <button type="button" onClick={() => setSuccess("")}>
            Dismiss
          </button>
        </div>
      )}

      {canManageClients && (
        <section className="clients-panel">
          <div className="clients-panel-heading">
            <div>
              <p className="clients-eyebrow">
                {editingId !== null ? "UPDATE RECORD" : "CLIENT DIRECTORY"}
              </p>
              <h2>{editingId !== null ? "Edit client" : "Add a client"}</h2>
              <p>Enter the client's name and any available contact details.</p>
            </div>

            {editingId !== null && (
              <button
                type="button"
                className="clients-button clients-button-secondary"
                onClick={resetForm}
              >
                Cancel edit
              </button>
            )}
          </div>

          <form className="clients-form" onSubmit={handleSubmit}>
            <div className="clients-form-grid">
              <div className="clients-field">
                <label htmlFor="client-name">Client name *</label>
                <input
                  id="client-name"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  maxLength={150}
                  required
                  placeholder="Client name"
                />
              </div>

              <div className="clients-field">
                <label htmlFor="client-company">Company</label>
                <input
                  id="client-company"
                  name="company"
                  value={form.company}
                  onChange={handleChange}
                  maxLength={150}
                  placeholder="Company or organization"
                />
              </div>

              <div className="clients-field">
                <label htmlFor="client-email">Email</label>
                <input
                  id="client-email"
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="contact@example.com"
                />
              </div>

              <div className="clients-field">
                <label htmlFor="client-phone">Phone</label>
                <input
                  id="client-phone"
                  name="phone"
                  type="tel"
                  value={form.phone}
                  onChange={handleChange}
                  maxLength={30}
                  placeholder="Contact number"
                />
              </div>

              <div className="clients-field clients-field-full">
                <label htmlFor="client-notes">Notes</label>
                <textarea
                  id="client-notes"
                  name="notes"
                  value={form.notes}
                  onChange={handleChange}
                  rows={3}
                  placeholder="Optional notes"
                />
              </div>
            </div>

            <div className="clients-form-actions">
              <button
                type="submit"
                className="clients-button clients-button-primary"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingId !== null
                    ? "Save changes"
                    : "Create client"}
              </button>

              {editingId !== null && (
                <button
                  type="button"
                  className="clients-button clients-button-secondary"
                  onClick={resetForm}
                  disabled={saving}
                >
                  Discard changes
                </button>
              )}
            </div>
          </form>
        </section>
      )}

      <section className="clients-panel">
        <div className="clients-list-heading">
          <div>
            <h2>Client directory</h2>
            <p>
              {loading
                ? "Loading clients..."
                : `${filteredClients.length} ${
                    filteredClients.length === 1 ? "client" : "clients"
                  } shown`}
            </p>
          </div>

          <div className="clients-search">
            <label className="visually-hidden" htmlFor="client-search">
              Search clients
            </label>
            <input
              id="client-search"
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search clients"
            />
          </div>
        </div>

        {loading ? (
          <div className="clients-state" aria-live="polite">
            Loading client records...
          </div>
        ) : filteredClients.length === 0 ? (
          <div className="clients-empty">
            <div className="clients-empty-mark" aria-hidden="true">
              C
            </div>
            <h3>{search ? "No matching clients" : "No clients available yet"}</h3>
            <p>
              {search
                ? "Try another name, company, email, or phone number."
                : canManageClients
                  ? "Create a client above to start organizing client projects."
                  : "Clients will appear here when they are connected to projects you can access."}
            </p>
          </div>
        ) : (
          <div className="clients-table-wrap">
            <table className="clients-table">
              <thead>
                <tr>
                  <th scope="col">Client</th>
                  <th scope="col">Contact</th>
                  <th scope="col">Phone</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredClients.map((client) => (
                  <tr key={client.id}>
                    <td>
                      <div className="clients-name">{client.name}</div>
                      <div className="clients-company">
                        {client.company || "Company not specified"}
                      </div>
                    </td>

                    <td>
                      {client.email ? (
                        <a href={`mailto:${client.email}`}>{client.email}</a>
                      ) : (
                        <span className="clients-muted">No email</span>
                      )}
                    </td>

                    <td>
                      {client.phone || (
                        <span className="clients-muted">—</span>
                      )}
                    </td>

                    <td>
                      <div className="clients-row-actions">
                        <button
                          type="button"
                          className="clients-text-button"
                          onClick={() => handleViewStatistics(client)}
                        >
                          {selectedId === client.id ? "Hide stats" : "View stats"}
                        </button>

                        {canManageClients && (
                          <>
                            <button
                              type="button"
                              className="clients-text-button"
                              onClick={() => handleEdit(client)}
                            >
                              Edit
                            </button>

                            <button
                              type="button"
                              className="clients-text-button clients-delete-button"
                              onClick={() => handleDelete(client)}
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {selectedId !== null && (
              <section className="clients-stats" aria-live="polite">
                {statisticsLoading ? (
                  <p className="clients-state">
                    Loading client statistics...
                  </p>
                ) : statistics ? (
                  <>
                    <p className="clients-eyebrow">CLIENT OVERVIEW</p>
                    <h3>
                      {statistics.client?.name || "Client statistics"}
                    </h3>

                    <div className="clients-stats-grid">
                      <article>
                        <span>Projects</span>
                        <strong>{statistics.total_projects ?? 0}</strong>
                      </article>
                      <article>
                        <span>Active projects</span>
                        <strong>{statistics.active_projects ?? 0}</strong>
                      </article>
                      <article>
                        <span>Completed projects</span>
                        <strong>{statistics.completed_projects ?? 0}</strong>
                      </article>
                      <article>
                        <span>Tracked time</span>
                        <strong>{formatHours(statistics.total_hours)}</strong>
                      </article>
                    </div>
                  </>
                ) : null}
              </section>
            )}
          </div>
        )}
      </section>
    </section>
  );
}

export default Clients;