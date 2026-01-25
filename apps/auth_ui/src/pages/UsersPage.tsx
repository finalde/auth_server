import { useState, useEffect } from 'react';
import { usersApi } from '../services/api';
import type { User, CreateUser, UpdateUser } from '../types';
import './Page.css';
import './EntityPage.css';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<CreateUser | UpdateUser>({
    username: '',
    email: '',
    password: '',
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await usersApi.getAll();
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await usersApi.create(formData as CreateUser);
      setShowForm(false);
      setFormData({ username: '', email: '', password: '' });
      loadUsers();
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    try {
      await usersApi.update(editingUser.user_id, formData as UpdateUser);
      setShowForm(false);
      setEditingUser(null);
      setFormData({ username: '', email: '', password: '' });
      loadUsers();
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      await usersApi.delete(userId);
      loadUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  const startEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
    });
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
    setEditingUser(null);
    setFormData({ username: '', email: '', password: '' });
  };

  if (loading) return <div className="page">Loading...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Users</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>Create User</button>
      </div>

      {showForm && (
        <div className="form-modal">
          <div className="form-content">
            <h2>{editingUser ? 'Edit User' : 'Create User'}</h2>
            <form onSubmit={editingUser ? handleUpdate : handleCreate}>
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={formData.username || ''}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              {!editingUser && (
                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    value={(formData as CreateUser).password || ''}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required={!editingUser}
                  />
                </div>
              )}
              <div className="form-group">
                <label>First Name</label>
                <input
                  type="text"
                  value={formData.first_name || ''}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input
                  type="text"
                  value={formData.last_name || ''}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary">{editingUser ? 'Update' : 'Create'}</button>
                <button type="button" className="btn-secondary" onClick={cancelForm}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="entity-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Name</th>
              <th>Status</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '24px' }}>
                  No users found. Click "Create User" to add one.
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.user_id}>
                  <td>{user.user_id}</td>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td>{user.first_name || ''} {user.last_name || ''}</td>
                  <td>{user.status}</td>
                  <td>{user.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button className="btn-small" onClick={() => startEdit(user)}>Edit</button>
                    <button className="btn-small btn-danger" onClick={() => handleDelete(user.user_id)}>Delete</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
