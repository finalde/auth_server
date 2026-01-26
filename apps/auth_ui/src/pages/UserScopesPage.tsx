import { useEffect, useState } from 'react';
import { userScopesApi } from '../services/api';
import type { CreateUserScope, UpdateUserScope, UserScope } from '../types';
import './Page.css';
import './EntityPage.css';

type FormState = CreateUserScope & UpdateUserScope;

export default function UserScopesPage() {
  const [scopes, setScopes] = useState<UserScope[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingScope, setEditingScope] = useState<UserScope | null>(null);
  const [formData, setFormData] = useState<FormState>({
    user_id: '',
    scope_name: '',
    is_active: true,
  });

  useEffect(() => {
    loadScopes();
  }, []);

  const loadScopes = async () => {
    try {
      setLoading(true);
      const data = await userScopesApi.getAll();
      setScopes(data);
    } catch (error) {
      console.error('Failed to load user scopes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await userScopesApi.create({
        user_id: formData.user_id,
        scope_name: formData.scope_name,
      });
      resetForm();
      loadScopes();
    } catch (error) {
      console.error('Failed to create user scope:', error);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingScope) return;
    try {
      await userScopesApi.update(editingScope.user_id, editingScope.scope_name, {
        is_active: formData.is_active,
      });
      resetForm();
      loadScopes();
    } catch (error) {
      console.error('Failed to update user scope:', error);
    }
  };

  const handleDelete = async (userId: string, scopeName: string) => {
    if (!confirm('Are you sure you want to delete this user scope?')) return;
    try {
      await userScopesApi.delete(userId, scopeName);
      loadScopes();
    } catch (error) {
      console.error('Failed to delete user scope:', error);
    }
  };

  const startEdit = (scope: UserScope) => {
    setEditingScope(scope);
    setFormData({
      user_id: scope.user_id,
      scope_name: scope.scope_name,
      is_active: scope.is_active,
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingScope(null);
    setFormData({
      user_id: '',
      scope_name: '',
      is_active: true,
    });
  };

  if (loading) return <div className="page">Loading...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>User Scopes</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>Assign Scope</button>
      </div>

      {showForm && (
        <div className="form-modal">
          <div className="form-content">
            <h2>{editingScope ? 'Edit User Scope' : 'Assign Scope'}</h2>
            <form onSubmit={editingScope ? handleUpdate : handleCreate}>
              <div className="form-group">
                <label>User ID</label>
                <input
                  type="text"
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  required
                  disabled={!!editingScope}
                />
              </div>
              <div className="form-group">
                <label>Scope Name</label>
                <input
                  type="text"
                  value={formData.scope_name}
                  onChange={(e) => setFormData({ ...formData, scope_name: e.target.value })}
                  required
                  disabled={!!editingScope}
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={!!formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  Active
                </label>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary">
                  {editingScope ? 'Update' : 'Create'}
                </button>
                <button type="button" className="btn-secondary" onClick={resetForm}>
                  Cancel
                </button>
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
              <th>Scope Name</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {scopes.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', padding: '24px' }}>
                  No user scopes found. Click "Assign Scope" to add one.
                </td>
              </tr>
            ) : (
              scopes.map((scope) => (
                <tr key={`${scope.user_id}:${scope.scope_name}`}>
                  <td>{scope.user_id}</td>
                  <td>{scope.scope_name}</td>
                  <td>{scope.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button className="btn-small" onClick={() => startEdit(scope)}>Edit</button>
                    <button
                      className="btn-small btn-danger"
                      onClick={() => handleDelete(scope.user_id, scope.scope_name)}
                    >
                      Delete
                    </button>
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
