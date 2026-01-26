import { useEffect, useState } from 'react';
import { userClaimsApi } from '../services/api';
import type { CreateUserClaim, UpdateUserClaim, UserClaim } from '../types';
import './Page.css';
import './EntityPage.css';

type FormState = CreateUserClaim & UpdateUserClaim;

export default function UserClaimsPage() {
  const [claims, setClaims] = useState<UserClaim[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingClaim, setEditingClaim] = useState<UserClaim | null>(null);
  const [formData, setFormData] = useState<FormState>({
    user_id: '',
    claim_name: '',
    claim_value: '',
    claim_type: '',
    is_active: true,
  });

  useEffect(() => {
    loadClaims();
  }, []);

  const loadClaims = async () => {
    try {
      setLoading(true);
      const data = await userClaimsApi.getAll();
      setClaims(data);
    } catch (error) {
      console.error('Failed to load user claims:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await userClaimsApi.create({
        user_id: formData.user_id,
        claim_name: formData.claim_name,
        claim_value: formData.claim_value,
        claim_type: formData.claim_type || undefined,
      });
      resetForm();
      loadClaims();
    } catch (error) {
      console.error('Failed to create user claim:', error);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingClaim) return;
    try {
      await userClaimsApi.update(editingClaim.user_id, editingClaim.claim_name, {
        claim_value: formData.claim_value,
        claim_type: formData.claim_type || undefined,
        is_active: formData.is_active,
      });
      resetForm();
      loadClaims();
    } catch (error) {
      console.error('Failed to update user claim:', error);
    }
  };

  const handleDelete = async (userId: string, claimName: string) => {
    if (!confirm('Are you sure you want to delete this user claim?')) return;
    try {
      await userClaimsApi.delete(userId, claimName);
      loadClaims();
    } catch (error) {
      console.error('Failed to delete user claim:', error);
    }
  };

  const startEdit = (claim: UserClaim) => {
    setEditingClaim(claim);
    setFormData({
      user_id: claim.user_id,
      claim_name: claim.claim_name,
      claim_value: claim.claim_value,
      claim_type: claim.claim_type || '',
      is_active: claim.is_active,
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingClaim(null);
    setFormData({
      user_id: '',
      claim_name: '',
      claim_value: '',
      claim_type: '',
      is_active: true,
    });
  };

  if (loading) return <div className="page">Loading...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>User Claims</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>Create Claim</button>
      </div>

      {showForm && (
        <div className="form-modal">
          <div className="form-content">
            <h2>{editingClaim ? 'Edit Claim' : 'Create Claim'}</h2>
            <form onSubmit={editingClaim ? handleUpdate : handleCreate}>
              <div className="form-group">
                <label>User ID</label>
                <input
                  type="text"
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  required
                  disabled={!!editingClaim}
                />
              </div>
              <div className="form-group">
                <label>Claim Name</label>
                <input
                  type="text"
                  value={formData.claim_name}
                  onChange={(e) => setFormData({ ...formData, claim_name: e.target.value })}
                  required
                  disabled={!!editingClaim}
                />
              </div>
              <div className="form-group">
                <label>Claim Value</label>
                <input
                  type="text"
                  value={formData.claim_value}
                  onChange={(e) => setFormData({ ...formData, claim_value: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Claim Type</label>
                <input
                  type="text"
                  value={formData.claim_type}
                  onChange={(e) => setFormData({ ...formData, claim_type: e.target.value })}
                  placeholder="string, number, boolean, json"
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
                  {editingClaim ? 'Update' : 'Create'}
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
              <th>Claim Name</th>
              <th>Value</th>
              <th>Type</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {claims.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '24px' }}>
                  No user claims found. Click "Create Claim" to add one.
                </td>
              </tr>
            ) : (
              claims.map((claim) => (
                <tr key={`${claim.user_id}:${claim.claim_name}`}>
                  <td>{claim.user_id}</td>
                  <td>{claim.claim_name}</td>
                  <td>{claim.claim_value}</td>
                  <td>{claim.claim_type || '-'}</td>
                  <td>{claim.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button className="btn-small" onClick={() => startEdit(claim)}>Edit</button>
                    <button
                      className="btn-small btn-danger"
                      onClick={() => handleDelete(claim.user_id, claim.claim_name)}
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
