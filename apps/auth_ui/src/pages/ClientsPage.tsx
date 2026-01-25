import { useState, useEffect } from 'react';
import { clientsApi } from '../services/api';
import type { Client, CreateClient, UpdateClient } from '../types';
import './Page.css';
import './EntityPage.css';

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<CreateClient>({
    client_name: '',
    redirect_uris: [],
    grant_types: [],
    response_types: [],
    scopes: [],
  });

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      const data = await clientsApi.getAll();
      setClients(data);
    } catch (error) {
      console.error('Failed to load clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await clientsApi.create(formData);
      setShowForm(false);
      setFormData({ client_name: '', redirect_uris: [], grant_types: [], response_types: [], scopes: [] });
      loadClients();
    } catch (error) {
      console.error('Failed to create client:', error);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingClient) return;
    try {
      await clientsApi.update(editingClient.client_id, formData as UpdateClient);
      setShowForm(false);
      setEditingClient(null);
      setFormData({ client_name: '', redirect_uris: [], grant_types: [], response_types: [], scopes: [] });
      loadClients();
    } catch (error) {
      console.error('Failed to update client:', error);
    }
  };

  const handleDelete = async (clientId: string) => {
    if (!confirm('Are you sure you want to delete this client?')) return;
    try {
      await clientsApi.delete(clientId);
      loadClients();
    } catch (error) {
      console.error('Failed to delete client:', error);
    }
  };

  const startEdit = (client: Client) => {
    setEditingClient(client);
    setFormData({
      client_name: client.client_name || '',
      client_uri: client.client_uri,
      redirect_uris: client.redirect_uris,
      grant_types: client.grant_types,
      response_types: client.response_types,
      scopes: client.scopes,
      logo_uri: client.logo_uri,
      tos_uri: client.tos_uri,
      policy_uri: client.policy_uri,
    });
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
    setEditingClient(null);
    setFormData({ client_name: '', redirect_uris: [], grant_types: [], response_types: [], scopes: [] });
  };

  if (loading) return <div className="page">Loading...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Clients</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>Create Client</button>
      </div>

      {showForm && (
        <div className="form-modal">
          <div className="form-content">
            <h2>{editingClient ? 'Edit Client' : 'Create Client'}</h2>
            <form onSubmit={editingClient ? handleUpdate : handleCreate}>
              <div className="form-group">
                <label>Client Name</label>
                <input
                  type="text"
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Redirect URIs (comma-separated)</label>
                <input
                  type="text"
                  value={formData.redirect_uris?.join(', ') || ''}
                  onChange={(e) => setFormData({ ...formData, redirect_uris: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                />
              </div>
              <div className="form-group">
                <label>Grant Types (comma-separated)</label>
                <input
                  type="text"
                  value={formData.grant_types?.join(', ') || ''}
                  onChange={(e) => setFormData({ ...formData, grant_types: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
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
              <div className="form-actions">
                <button type="submit" className="btn-primary">{editingClient ? 'Update' : 'Create'}</button>
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
              <th>Client ID</th>
              <th>Name</th>
              <th>Grant Types</th>
              <th>Scopes</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {clients.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '24px' }}>
                  No clients found. Click "Create Client" to add one.
                </td>
              </tr>
            ) : (
              clients.map((client) => (
                <tr key={client.client_id}>
                  <td>{client.client_id}</td>
                  <td>{client.client_name || '-'}</td>
                  <td>{client.grant_types.join(', ') || '-'}</td>
                  <td>{client.scopes.join(', ') || '-'}</td>
                  <td>{client.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button className="btn-small" onClick={() => startEdit(client)}>Edit</button>
                    <button className="btn-small btn-danger" onClick={() => handleDelete(client.client_id)}>Delete</button>
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
