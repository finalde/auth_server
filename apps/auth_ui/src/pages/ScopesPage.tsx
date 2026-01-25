import { useState, useEffect } from 'react';
import { scopesApi } from '../services/api';
import type { Scope, CreateScope } from '../types';
import './Page.css';
import './EntityPage.css';

export default function ScopesPage() {
  const [scopes, setScopes] = useState<Scope[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingScope, setEditingScope] = useState<Scope | null>(null);
  const [formData, setFormData] = useState<CreateScope>({
    scope_name: '',
    description: '',
  });

  useEffect(() => {
    loadScopes();
  }, []);

  const loadScopes = async () => {
    try {
      setLoading(true);
      const data = await scopesApi.getAll();
      setScopes(data);
    } catch (error) {
      console.error('Failed to load scopes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await scopesApi.create(formData);
      setShowForm(false);
      setFormData({ scope_name: '', description: '' });
      loadScopes();
    } catch (error) {
      console.error('Failed to create scope:', error);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingScope) return;
    try {
      await scopesApi.update(editingScope.scope_name, { description: formData.description });
      setShowForm(false);
      setEditingScope(null);
      setFormData({ scope_name: '', description: '' });
      loadScopes();
    } catch (error) {
      console.error('Failed to update scope:', error);
    }
  };

  const handleDelete = async (scopeName: string) => {
    if (!confirm('Are you sure you want to delete this scope?')) return;
    try {
      await scopesApi.delete(scopeName);
      loadScopes();
    } catch (error) {
      console.error('Failed to delete scope:', error);
    }
  };

  const startEdit = (scope: Scope) => {
    setEditingScope(scope);
    setFormData({
      scope_name: scope.scope_name,
      description: scope.description || '',
    });
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
    setEditingScope(null);
    setFormData({ scope_name: '', description: '' });
  };

  if (loading) return <div className="page">Loading...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Scopes</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>Create Scope</button>
      </div>

      {showForm && (
        <div className="form-modal">
          <div className="form-content">
            <h2>{editingScope ? 'Edit Scope' : 'Create Scope'}</h2>
            <form onSubmit={editingScope ? handleUpdate : handleCreate}>
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
                <label>Description</label>
                <textarea
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary">{editingScope ? 'Update' : 'Create'}</button>
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
              <th>Scope Name</th>
              <th>Description</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {scopes.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', padding: '24px' }}>
                  No scopes found. Click "Create Scope" to add one.
                </td>
              </tr>
            ) : (
              scopes.map((scope) => (
                <tr key={scope.scope_name}>
                  <td>{scope.scope_name}</td>
                  <td>{scope.description || '-'}</td>
                  <td>{scope.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button className="btn-small" onClick={() => startEdit(scope)}>Edit</button>
                    <button className="btn-small btn-danger" onClick={() => handleDelete(scope.scope_name)}>Delete</button>
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
