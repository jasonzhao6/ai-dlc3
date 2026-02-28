import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr('');
    setLoading(true);
    try {
      const data = await api.login(username, password);
      login(data);
      navigate('/');
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-bg d-flex align-items-center justify-content-center">
      <div className="card p-4 shadow-lg" style={{ width: '100%', maxWidth: 400, borderRadius: 16 }}>
        <div className="text-center mb-4">
          <i className="bi bi-cloud-arrow-up-fill text-success" style={{ fontSize: 48 }}></i>
          <h3 className="mt-2 fw-bold" style={{ color: '#2d6a4f' }}>FileShare</h3>
          <p className="text-muted small">Sign in to your account</p>
        </div>
        {err && <div className="alert alert-danger py-2 small">{err}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label small fw-semibold">Username</label>
            <div className="input-group">
              <span className="input-group-text"><i className="bi bi-person"></i></span>
              <input type="text" className="form-control" value={username} onChange={e => setUsername(e.target.value)} required autoFocus />
            </div>
          </div>
          <div className="mb-4">
            <label className="form-label small fw-semibold">Password</label>
            <div className="input-group">
              <span className="input-group-text"><i className="bi bi-lock"></i></span>
              <input type="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>
          </div>
          <button type="submit" className="btn btn-forest w-100" disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2"></span> : <i className="bi bi-box-arrow-in-right me-2"></i>}
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
