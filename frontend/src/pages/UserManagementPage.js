import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [form, setForm] = useState({ username: '', password: '', role: 'viewer' });

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await api.getUsers();
      setUsers(data.users || []);
    } catch (ex) { setErr(ex.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadUsers(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setErr('');
    try {
      await api.createUser(form);
      setShowForm(false);
      setForm({ username: '', password: '', role: 'viewer' });
      loadUsers();
    } catch (ex) { setErr(ex.message); }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setErr('');
    try {
      const data = {};
      if (form.role) data.role = form.role;
      if (form.password) data.password = form.password;
      await api.updateUser(editUser, data);
      setEditUser(null);
      setShowForm(false);
      setForm({ username: '', password: '', role: 'viewer' });
      loadUsers();
    } catch (ex) { setErr(ex.message); }
  };

  const handleDelete = async (username) => {
    if (!window.confirm(`Delete user "${username}"?`)) return;
    try {
      await api.deleteUser(username);
      loadUsers();
    } catch (ex) { setErr(ex.message); }
  };

  const startEdit = (user) => {
    setEditUser(user.username);
    setForm({ username: user.username, password: '', role: user.role });
    setShowForm(true);
  };

  const roleBadge = (role) => {
    const colors = { admin: 'success', uploader: 'primary', reader: 'info', viewer: 'secondary' };
    return <span className={`badge bg-${colors[role] || 'dark'}`}>{role}</span>;
  };

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0" style={{ color: '#2d6a4f' }}><i className="bi bi-people me-2"></i>User Management</h4>
        <button className="btn btn-forest" onClick={() => { setEditUser(null); setForm({ username: '', password: '', role: 'viewer' }); setShowForm(!showForm); }}>
          <i className="bi bi-person-plus me-1"></i>New User
        </button>
      </div>

      {err && <div className="alert alert-danger py-2 small">{err}<button className="btn-close float-end" onClick={() => setErr('')}></button></div>}

      {showForm && (
        <div className="card mb-4">
          <div className="card-body">
            <h6 className="fw-semibold mb-3">{editUser ? `Edit: ${editUser}` : 'Create User'}</h6>
            <form onSubmit={editUser ? handleUpdate : handleCreate}>
              <div className="row g-3">
                {!editUser && (
                  <div className="col-md-3">
                    <input type="text" className="form-control" placeholder="Username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} required />
                  </div>
                )}
                <div className="col-md-3">
                  <input type="password" className="form-control" placeholder={editUser ? 'New password (optional)' : 'Password'} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required={!editUser} />
                </div>
                <div className="col-md-3">
                  <select className="form-select" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
                    <option value="viewer">Viewer</option>
                    <option value="reader">Reader</option>
                    <option value="uploader">Uploader</option>
                  </select>
                </div>
                <div className="col-md-3">
                  <button type="submit" className="btn btn-forest me-2">{editUser ? 'Update' : 'Create'}</button>
                  <button type="button" className="btn btn-outline-secondary" onClick={() => { setShowForm(false); setEditUser(null); }}>Cancel</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-5"><span className="spinner-border text-success"></span></div>
      ) : (
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover mb-0">
              <thead style={{ backgroundColor: '#e9f5ef' }}>
                <tr>
                  <th>Username</th>
                  <th>Role</th>
                  <th>Assigned Folders</th>
                  <th style={{ width: 150 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.username}>
                    <td className="fw-semibold"><i className="bi bi-person me-1"></i>{u.username}</td>
                    <td>{roleBadge(u.role)}</td>
                    <td><span className="text-muted small">{(u.assignedFolders || []).length} folder(s)</span></td>
                    <td>
                      {u.username !== 'admin' && (
                        <>
                          <button className="btn btn-sm btn-outline-forest me-1" onClick={() => startEdit(u)} title="Edit"><i className="bi bi-pencil"></i></button>
                          <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(u.username)} title="Delete"><i className="bi bi-trash"></i></button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
                {users.length === 0 && <tr><td colSpan="4" className="text-center text-muted py-4">No users found</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
