function EmployeeHeader() {
  return (
    <header className="employee-header">
      <div className="employee-header-left">
        <div>
          <p className="employee-header-eyebrow">
            Workspace
          </p>

          <h1 className="employee-header-title">
            Dashboard
          </h1>
        </div>
      </div>

      <div className="employee-header-right">
        <span className="employee-header-status">
          Employee
        </span>
      </div>
    </header>
  );
}

export default EmployeeHeader;