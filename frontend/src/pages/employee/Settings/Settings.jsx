
import useAuth from "../../../hooks/useAuth";
import "../../../styles/settings.css";

function Settings() {
  const { user } = useAuth();

  const fullName =
    [user?.first_name, user?.last_name].filter(Boolean).join(" ") ||
    user?.full_name ||
    user?.username ||
    "Your account";

  const accountFields = [
    { label: "Full name", value: fullName },
    { label: "Username", value: user?.username || "Not provided" },
    { label: "Email address", value: user?.email || "Not provided" },
    { label: "Role", value: user?.role || "Not provided" },
  ];

  return (
    <div className="settings-page">
      <header className="settings-page-header">
        <div>
          <p className="settings-eyebrow">Account</p>
          <h2>Settings</h2>
          <p className="settings-description">
            View your account information and settings availability.
          </p>
        </div>
      </header>

      <section className="settings-panel">
        <div className="settings-panel-heading">
          <div className="settings-panel-icon" aria-hidden="true">
            {fullName.charAt(0).toUpperCase()}
          </div>

          <div>
            <h3>Account information</h3>
            <p>Your current ChronoTrack account details.</p>
          </div>
        </div>

        <div className="settings-details">
          {accountFields.map((field) => (
            <div className="settings-detail-row" key={field.label}>
              <span>{field.label}</span>
              <strong>{field.value}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="settings-panel">
        <div className="settings-panel-heading">
          <div className="settings-panel-icon" aria-hidden="true">
            ⚙
          </div>

          <div>
            <h3>Preferences</h3>
            <p>Personalize your ChronoTrack experience.</p>
          </div>
        </div>

        <div className="settings-notice">
          Editable preferences are not available yet. Your account information
          above is displayed for reference and is not changed from this page.
        </div>
      </section>
    </div>
  );
}

export default Settings;
