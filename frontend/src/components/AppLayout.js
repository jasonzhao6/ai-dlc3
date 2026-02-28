import React, { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';
import ChangePasswordModal from './ChangePasswordModal';

export default function AppLayout() {
  const { session, logout } = useAuth();
  const navigate = useNavigate();
  const [showPwModal, setShowPwModal] = useState(session?.mustChangePassword || false);

  const handleLogout = async () => {
    try { await api.logout(); } catch {}
    logout();
    navigate('/login');
  };

  const isAdmin = session?.role === 'admin';

  return (
    <div className="d-flex flex-column min-vh-100">
      <nav className="navbar navbar-expand-lg navbar-dark" style={{ backgroundColor: '#2d6a4f' }}>
        <div className="container-fluid">
          <Link className="navbar-brand fw-bold" to="/">
            <i className="bi bi-cloud-arrow-up-fill me-2"></i>FileShare
          </Link>
          <div className="navbar-nav me-auto">
            <Link className="nav-link" to="/"><i className="bi bi-folder2-open me-1"></i>Files</Link>
            {isAdmin && <Link className="nav-link" to="/users"><i className="bi bi-people me-1"></i>Users</Link>}
            {isAdmin && <Link className="nav-link" to="/folders"><i className="bi bi-folder-plus me-1"></i>Folders</Link>}
          </div>
          <div className="navbar-nav">
            <span className="nav-link text-light opacity-75">
              <i className="bi bi-person-circle me-1"></i>{session?.username}
              <span className="badge bg-light text-dark ms-2">{session?.role}</span>
            </span>
            <button className="btn btn-outline-light btn-sm ms-2" onClick={() => setShowPwModal(true)}>
              <i className="bi bi-key me-1"></i>Password
            </button>
            <button className="btn btn-outline-light btn-sm ms-2" onClick={handleLogout}>
              <i className="bi bi-box-arrow-right me-1"></i>Logout
            </button>
          </div>
        </div>
      </nav>
      <main className="container-fluid flex-grow-1 py-4" style={{ backgroundColor: '#f8f9fa' }}>
        <Outlet />
      </main>
      {showPwModal && <ChangePasswordModal onClose={() => setShowPwModal(false)} forced={session?.mustChangePassword} />}
    </div>
  );
}
