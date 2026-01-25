import { useState, useEffect } from 'react';
import { resourcesApi } from '../services/api';
import type { Resource, CreateResource, UpdateResource } from '../types';
import './Page.css';
import './EntityPage.css';

export default function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingResource, setEditingResource] = useState<Resource | null>(null);
  const [formData, setFormData] = useState<CreateResource>({
    resource_name: '',
    resource_uri: '',
    scopes: [],
    description: '',
  });

  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = async () => {
    try {
      setLoading(true);
      const data = await resourcesApi.getAll();
      setResources(data);
    } catch (error) {
      console.error('Failed to load resources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await resourcesApi.create(formData);
      setShowForm(false);
      setFormData({ resource_name: '', resource_uri: '', scopes: [], description: '' });
      loadResources();
    } catch (error) {
      console.error('Failed to create resource:', error);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingResource) return;
    try {
      await resourcesApi.update(editingResource.resource_id, formData as UpdateResource);
      setShowForm(false);
      setEditingResource(null);
      setFormData({ resource_name: '', resource_uri: '', scopes: [], description: '' });
      loadResources();
    } catch (error) {
      console.error('Failed to update resource:', error);
    }
  };

  const handleDelete = async (resourceId: string) => {
    if (!confirm('Are you sure you want to delete this resource?')) return;
    try {
      await resourcesApi.delete(resourceId);
      loadResources();
    } catch (error) {
      console.error('Failed to delete resource:', error);
    }
  };

  const startEdit = (resource: Resource) => {
    setEditingResource(resource);
    setFormData({
      resource_name: resource.resource_name,
      resource_uri: resource.resource_uri,
      scopes: resource.scopes,
      description: resource.description || '',
    });
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
    setEditingResource(null);
    setFormData({ resource_name: '', resource_uri: '', scopes: [], description: '' });
  };

  if (loading) return <div className="page">Loading...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Resources</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>Create Resource</button>
      </div>

      {showForm && (
        <div className="form-modal">
          <div className="form-content">
            <h2>{editingResource ? 'Edit Resource' : 'Create Resource'}</h2>
            <form onSubmit={editingResource ? handleUpdate : handleCreate}>
              <div className="form-group">
                <label>Resource Name</label>
                <input
                  type="text"
                  value={formData.resource_name}
                  onChange={(e) => setFormData({ ...formData, resource_name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Resource URI</label>
                <input
                  type="text"
                  value={formData.resource_uri}
                  onChange={(e) => setFormData({ ...formData, resource_uri: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Scopes (comma-separated)</label>
                <input
                  type="text"
                  value={formData.scopes?.join(', ') || ''}
                  onChange={(e) => setFormData({ ...formData, scopes: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
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
                <button type="submit" className="btn-primary">{editingResource ? 'Update' : 'Create'}</button>
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
              <th>Resource ID</th>
              <th>Name</th>
              <th>URI</th>
              <th>Scopes</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {resources.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '24px' }}>
                  No resources found. Click "Create Resource" to add one.
                </td>
              </tr>
            ) : (
              resources.map((resource) => (
                <tr key={resource.resource_id}>
                  <td>{resource.resource_id}</td>
                  <td>{resource.resource_name}</td>
                  <td>{resource.resource_uri}</td>
                  <td>{resource.scopes.join(', ') || '-'}</td>
                  <td>{resource.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button className="btn-small" onClick={() => startEdit(resource)}>Edit</button>
                    <button className="btn-small btn-danger" onClick={() => handleDelete(resource.resource_id)}>Delete</button>
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
