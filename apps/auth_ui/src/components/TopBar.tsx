import { logout } from '../services/auth';
import './TopBar.css';

export default function TopBar() {
  const handleLogout = () => {
    logout();
  };

  return (
    <header className="top-bar">
      <div className="top-bar-content">
        <h1 className="top-bar-title">Auth Server Admin</h1>
        <div className="top-bar-actions">
          <span className="user-info">Admin User</span>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </div>
    </header>
  );
}
