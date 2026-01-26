import { NavLink } from 'react-router-dom';
import './Sidebar.css';

export default function Sidebar() {
  return (
    <nav className="sidebar">
      <ul className="sidebar-menu">
        <li>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>
            Dashboard
          </NavLink>
        </li>
        <li>
          <NavLink to="/clients" className={({ isActive }) => isActive ? 'active' : ''}>
            Clients
          </NavLink>
        </li>
        <li>
          <NavLink to="/users" className={({ isActive }) => isActive ? 'active' : ''}>
            Users
          </NavLink>
        </li>
        <li>
          <NavLink to="/resources" className={({ isActive }) => isActive ? 'active' : ''}>
            Resources
          </NavLink>
        </li>
        <li>
          <NavLink to="/scopes" className={({ isActive }) => isActive ? 'active' : ''}>
            Scopes
          </NavLink>
        </li>
        <li>
          <NavLink to="/user-claims" className={({ isActive }) => isActive ? 'active' : ''}>
            User Claims
          </NavLink>
        </li>
        <li>
          <NavLink to="/user-scopes" className={({ isActive }) => isActive ? 'active' : ''}>
            User Scopes
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}
