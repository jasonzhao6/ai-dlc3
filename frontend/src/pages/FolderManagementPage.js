import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function FolderManagementPage() {
  const [folders, setFolders] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [newFolder, setNewFolder] = useState({ folderName: '', parentFolderId: '' });
  const [assignForm, setAssignForm] = useState({ username: '', folderIds: [] });
  const [showAssign, setShowAssign] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [fData, uData] = await Promise.all([api.getFolders(), api.getUsers()]);
      setFolders(fData.folders || []);
      setUsers(uData.users || []);
    } catch (ex) { setErr(ex.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setErr('');
    try {
      const data = { folderName: newFolder.folderName };
      if (newFolder.parentFolderId) data.parentFolderId = newFolder.parentFolderId;
      await api.createFolder(data);
      setNewFolder({ folderName: '', parentFolderId: '' });
      load();
    } catch (ex) { setErr(ex.message); }
  };

  const handleDelete = async (folderId, folderName) => {
    if (!window.confirm(`Delete folder "${folderName}" and all its contents?`)) return;
    try {
      await api.deleteFolder(folderId);
      load();
    } catch (ex) { setErr(ex.message); }
  };

  const handleAssign = async (e) => {
    e.preventDefault();
    setErr('');
    try {
      await api.assignFolders({ username: assignForm.username, folderIds: assignForm.folderIds });
      setShowAssign(false);
      setAssignForm({ username: '', folderIds: [] });
      load();
    } catch (ex) { setErr(ex.message); }
  };

  const handleUnassign = async (username, folderId) => {
    try {
      await api.unassignFolders({ username, folderIds: [folderId] });
      load();
    } catch (ex) { setErr(ex.message); }
  };

  const toggleFolderSelection = (folderId) => {
    setAssignForm(prev => ({
      ...prev,
      folderIds: prev.folderIds.includes(folderId)
        ? prev.folderIds.filter(id => id !== folderId)
        : [...prev.folderIds, folderId],
    }));
  };

  // Build tree
  const buildTree = (parentId = 'ROOT', depth = 0) => {
    return folders
      .filter(f => (f.parentFolderId || 'ROOT') === parentId)
      .map(f => (
        <React.Fragment key={f.folderId}>
          <tr>
            <td style={{ paddingLeft: 20 + depth * 24 }}>
              <i className={`bi bi-folder-fill me-2 ${depth === 0 ? 'text-warning' : 'text-muted'}`}></i>
              <span className="fw-semibold">{f.folderName}</span>
            </td>
            <td>
              {(f.assignedUsers || []).map(u => (
                <span key={u} className="badge bg-light text-dark me-1">
                  {u}
                  <button className="btn-close btn-close-dark ms-1" style={{ fontSize: 8 }} onClick={() => handleUnassign(u, f.folderId)} title={`Unassign ${u}`}></button>
                </span>
              ))}
            </td>
            <td>
              <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(f.folderId, f.folderName)} title="Delete"><i className="bi bi-trash"></i></button>
            </td>
          </tr>
          {buildTree(f.folderId, depth + 1)}
        </React.Fragment>
      ));
  };

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0" style={{ color: '#2d6a4f' }}><i className="bi bi-folder-plus me-2"></i>Folder Management</h4>
        <button className="btn btn-forest" onClick={() => setShowAssign(!showAssign)}>
          <i className="bi bi-link-45deg me-1"></i>Assign Folders
        </button>
      </div>

      {err && <div className="alert alert-danger py-2 small">{err}<button className="btn-close float-end" onClick={() => setErr('')}></button></div>}

      {/* Create folder form */}
      <div className="card mb-4">
        <div className="card-body">
          <h6 className="fw-semibold mb-3">Create Folder</h6>
          <form onSubmit={handleCreate} className="row g-3">
            <div className="col-md-4">
              <input type="text" className="form-control" placeholder="Folder name" value={newFolder.folderName} onChange={e => setNewFolder({ ...newFolder, folderName: e.target.value })} required />
            </div>
            <div className="col-md-4">
              <select className="form-select" value={newFolder.parentFolderId} onChange={e => setNewFolder({ ...newFolder, parentFolderId: e.target.value })}>
                <option value="">Root (top level)</option>
                {folders.map(f => <option key={f.folderId} value={f.folderId}>{f.folderName}</option>)}
              </select>
            </div>
            <div className="col-md-4">
              <button type="submit" className="btn btn-forest"><i className="bi bi-plus-lg me-1"></i>Create</button>
            </div>
          </form>
        </div>
      </div>

      {/* Assign folders panel */}
      {showAssign && (
        <div className="card mb-4">
          <div className="card-body">
            <h6 className="fw-semibold mb-3">Assign Folders to User</h6>
            <form onSubmit={handleAssign}>
              <div className="row g-3 mb-3">
                <div className="col-md-4">
                  <select className="form-select" value={assignForm.username} onChange={e => setAssignForm({ ...assignForm, username: e.target.value })} required>
                    <option value="">Select user...</option>
                    {users.filter(u => u.role !== 'admin').map(u => <option key={u.username} value={u.username}>{u.username} ({u.role})</option>)}
                  </select>
                </div>
              </div>
              <div className="mb-3">
                {folders.map(f => (
                  <div key={f.folderId} className="form-check form-check-inline">
                    <input className="form-check-input" type="checkbox" checked={assignForm.folderIds.includes(f.folderId)} onChange={() => toggleFolderSelection(f.folderId)} />
                    <label className="form-check-label small">{f.folderName}</label>
                  </div>
                ))}
              </div>
              <button type="submit" className="btn btn-forest me-2" disabled={!assignForm.username || assignForm.folderIds.length === 0}>
                <i className="bi bi-link-45deg me-1"></i>Assign
              </button>
              <button type="button" className="btn btn-outline-secondary" onClick={() => setShowAssign(false)}>Cancel</button>
            </form>
          </div>
        </div>
      )}

      {/* Folder tree */}
      {loading ? (
        <div className="text-center py-5"><span className="spinner-border text-success"></span></div>
      ) : (
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover mb-0">
              <thead style={{ backgroundColor: '#e9f5ef' }}>
                <tr>
                  <th>Folder</th>
                  <th>Assigned Users</th>
                  <th style={{ width: 80 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {buildTree()}
                {folders.length === 0 && <tr><td colSpan="3" className="text-center text-muted py-4">No folders yet</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
