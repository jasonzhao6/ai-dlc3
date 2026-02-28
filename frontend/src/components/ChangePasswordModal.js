import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';

export default function ChangePasswordModal({ onClose, forced }) {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);
  const { clearMustChangePassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr('');
    setLoading(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      clearMustChangePassword();
      onClose();
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header" style={{ backgroundColor: '#2d6a4f', color: '#fff' }}>
            <h5 className="modal-title"><i className="bi bi-key me-2"></i>Change Password</h5>
            {!forced && <button className="btn-close btn-close-white" onClick={onClose}></button>}
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              {forced && <div className="alert alert-warning py-2 small"><i className="bi bi-exclamation-triangle me-1"></i>You must change your password before continuing.</div>}
              {err && <div className="alert alert-danger py-2 small">{err}</div>}
              <div className="mb-3">
                <label className="form-label small fw-semibold">Current Password</label>
                <input type="password" className="form-control" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} required />
              </div>
              <div className="mb-3">
                <label className="form-label small fw-semibold">New Password</label>
                <input type="password" className="form-control" value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
              </div>
            </div>
            <div className="modal-footer">
              {!forced && <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>}
              <button type="submit" className="btn btn-forest" disabled={loading}>
                {loading ? <span className="spinner-border spinner-border-sm me-2"></span> : null}
                Change Password
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
