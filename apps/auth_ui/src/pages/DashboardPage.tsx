import './Page.css';

export default function DashboardPage() {
  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p>Welcome to Auth Server Admin Panel</p>
      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>Clients</h3>
          <p>Manage OAuth2 clients</p>
        </div>
        <div className="stat-card">
          <h3>Users</h3>
          <p>Manage user accounts</p>
        </div>
        <div className="stat-card">
          <h3>Resources</h3>
          <p>Manage API resources</p>
        </div>
        <div className="stat-card">
          <h3>Scopes</h3>
          <p>Manage OAuth2 scopes</p>
        </div>
      </div>
    </div>
  );
}
