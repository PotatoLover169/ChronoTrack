import "../../styles/header.css";

function ManagerHeader() {
  return (
    <header className="employee-header">
      <div className="employee-header-left">
        <div>
          <p className="employee-header-eyebrow">
            Workspace
          </p>

          <h1 className="employee-header-title">
            Manager Dashboard
          </h1>
        </div>
      </div>

      <div className="employee-header-right">
        <span className="employee-header-status">
          Manager
        </span>
      </div>
    </header>
  );
}

export default ManagerHeader;