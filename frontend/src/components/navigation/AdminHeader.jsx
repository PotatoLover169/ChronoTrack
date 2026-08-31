import "../../styles/header.css";

function AdminHeader() {
  return (
    <header className="employee-header">
      <div className="employee-header-left">
        <div>
          <p className="employee-header-eyebrow">
            Organization
          </p>

          <h1 className="employee-header-title">
            Admin Dashboard
          </h1>
        </div>
      </div>

      <div className="employee-header-right">
        <span className="employee-header-status">
          Admin
        </span>
      </div>
    </header>
  );
}

export default AdminHeader;