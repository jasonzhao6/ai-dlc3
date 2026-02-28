import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';

const MAX_FILE_SIZE = 1073741824; // 1GB

function formatSize(bytes) {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++; }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function formatDate(ts) {
  if (!ts) return '';
  return new Date(ts * 1000).toLocaleString();
}

export default function FileBrowserPage() {
  const { session } = useAuth();
  const role = session?.role;
  const canUpload = role === 'admin' || role === 'uploader';
  const canDownload = role === 'admin' || role === 'reader';

  const [folders, setFolders] = useState([]);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [folderPath, setFolderPath] = useState([]);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [versions, setVersions] = useState(null);
  const [versionFile, setVersionFile] = useState('');

  const loadFolders = useCallback(async () => {
    try {
      const data = await api.getFolders();
      setFolders(data.folders || []);
    } catch (ex) { setErr(ex.message); }
  }, []);

  const loadFiles = useCallback(async (folderId) => {
    if (!folderId) { setFiles([]); return; }
    try {
      const data = await api.getFiles({ folderId, sortBy, sortOrder });
      setFiles(data.files || []);
    } catch (ex) { setErr(ex.message); }
  }, [sortBy, sortOrder]);

  useEffect(() => { loadFolders().finally(() => setLoading(false)); }, [loadFolders]);
  useEffect(() => { if (currentFolder) loadFiles(currentFolder.folderId); }, [currentFolder, loadFiles]);

  const navigateToFolder = (folder) => {
    setSearch('');
    setCurrentFolder(folder);
    setFolderPath(prev => [...prev, folder]);
  };

  const navigateUp = () => { // eslint-disable-line no-unused-vars
    const newPath = [...folderPath];
    newPath.pop();
    setCurrentFolder(newPath.length > 0 ? newPath[newPath.length - 1] : null);
    setFolderPath(newPath);
    if (newPath.length === 0) setFiles([]);
  };

  const navigateToBreadcrumb = (index) => {
    const newPath = folderPath.slice(0, index + 1);
    setCurrentFolder(newPath[newPath.length - 1]);
    setFolderPath(newPath);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!search.trim()) return;
    setErr('');
    try {
      const data = await api.getFiles({ search: search.trim(), sortBy, sortOrder });
      setFiles(data.files || []);
      setCurrentFolder(null);
      setFolderPath([]);
    } catch (ex) { setErr(ex.message); }
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    e.target.value = '';

    if (file.size > MAX_FILE_SIZE) {
      setErr('File exceeds maximum size of 1GB');
      return;
    }
    if (!currentFolder) {
      setErr('Navigate to a folder first');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setErr('');
    try {
      const urlData = await api.getUploadUrl({
        folderId: currentFolder.folderId,
        fileName: file.name,
        fileSize: file.size,
      });

      // Upload directly to S3
      const xhr = new XMLHttpRequest();
      xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable) setUploadProgress(Math.round((ev.loaded / ev.total) * 100));
      };
      await new Promise((resolve, reject) => {
        xhr.onload = () => xhr.status < 400 ? resolve() : reject(new Error('Upload failed'));
        xhr.onerror = () => reject(new Error('Upload failed'));
        xhr.open('PUT', urlData.uploadUrl);
        xhr.send(file);
      });

      loadFiles(currentFolder.folderId);
    } catch (ex) { setErr(ex.message); }
    finally { setUploading(false); }
  };

  const handleDownload = async (file, versionNumber) => {
    try {
      const data = await api.getDownloadUrl({
        folderId: file.folderId || currentFolder?.folderId,
        fileName: file.fileName,
        ...(versionNumber ? { versionNumber } : {}),
      });
      window.open(data.downloadUrl, '_blank');
    } catch (ex) { setErr(ex.message); }
  };

  const showVersions = async (file) => {
    try {
      const fid = file.folderId || currentFolder?.folderId;
      const data = await api.getVersions(fid, file.fileName);
      setVersions(data.versions || []);
      setVersionFile(file.fileName);
    } catch (ex) { setErr(ex.message); }
  };

  const childFolders = currentFolder
    ? folders.filter(f => f.parentFolderId === currentFolder.folderId)
    : folders.filter(f => !f.parentFolderId || f.parentFolderId === 'ROOT');

  const sortIcon = (field) => {
    if (sortBy !== field) return <i className="bi bi-arrow-down-up text-muted ms-1" style={{ fontSize: 12 }}></i>;
    return <i className={`bi bi-arrow-${sortOrder === 'asc' ? 'up' : 'down'} ms-1`} style={{ color: '#2d6a4f', fontSize: 12 }}></i>;
  };

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0" style={{ color: '#2d6a4f' }}><i className="bi bi-folder2-open me-2"></i>File Browser</h4>
        <form onSubmit={handleSearch} className="d-flex" style={{ maxWidth: 350 }}>
          <div className="input-group">
            <input type="text" className="form-control" placeholder="Search files..." value={search} onChange={e => setSearch(e.target.value)} />
            <button className="btn btn-outline-forest" type="submit"><i className="bi bi-search"></i></button>
            {search && <button className="btn btn-outline-secondary" type="button" onClick={() => { setSearch(''); if (currentFolder) loadFiles(currentFolder.folderId); }}><i className="bi bi-x"></i></button>}
          </div>
        </form>
      </div>

      {err && <div className="alert alert-danger py-2 small">{err}<button className="btn-close float-end" onClick={() => setErr('')}></button></div>}

      {/* Breadcrumb */}
      <nav className="mb-3">
        <ol className="breadcrumb mb-0">
          <li className="breadcrumb-item">
            <button className="btn btn-link p-0 text-decoration-none" style={{ color: '#2d6a4f' }} onClick={() => { setCurrentFolder(null); setFolderPath([]); setFiles([]); setSearch(''); }}>
              <i className="bi bi-house me-1"></i>Home
            </button>
          </li>
          {folderPath.map((f, i) => (
            <li key={f.folderId} className={`breadcrumb-item ${i === folderPath.length - 1 ? 'active' : ''}`}>
              {i < folderPath.length - 1
                ? <button className="btn btn-link p-0 text-decoration-none" style={{ color: '#2d6a4f' }} onClick={() => navigateToBreadcrumb(i)}>{f.folderName}</button>
                : f.folderName}
            </li>
          ))}
        </ol>
      </nav>

      {loading ? (
        <div className="text-center py-5"><span className="spinner-border text-success"></span></div>
      ) : (
        <>
          {/* Folders */}
          {childFolders.length > 0 && (
            <div className="card mb-4">
              <div className="card-body p-2">
                <div className="row g-2">
                  {childFolders.map(f => (
                    <div key={f.folderId} className="col-md-3 col-sm-6">
                      <div className="folder-item d-flex align-items-center" onClick={() => navigateToFolder(f)}>
                        <i className="bi bi-folder-fill text-warning me-2" style={{ fontSize: 20 }}></i>
                        <span className="fw-semibold small">{f.folderName}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Upload bar */}
          {canUpload && currentFolder && (
            <div className="mb-3 d-flex align-items-center">
              <label className="btn btn-forest me-3">
                <i className="bi bi-cloud-arrow-up me-1"></i>Upload File
                <input type="file" hidden onChange={handleUpload} disabled={uploading} />
              </label>
              {uploading && (
                <div className="flex-grow-1">
                  <div className="progress" style={{ height: 8 }}>
                    <div className="progress-bar bg-success" style={{ width: `${uploadProgress}%` }}></div>
                  </div>
                  <small className="text-muted">{uploadProgress}%</small>
                </div>
              )}
            </div>
          )}

          {/* Files table */}
          {(currentFolder || search) && (
            <div className="card">
              <div className="table-responsive">
                <table className="table table-hover mb-0">
                  <thead style={{ backgroundColor: '#e9f5ef' }}>
                    <tr>
                      <th role="button" onClick={() => handleSort('name')}>Name{sortIcon('name')}</th>
                      {search && <th>Folder</th>}
                      <th role="button" onClick={() => handleSort('fileSize')}>Size{sortIcon('fileSize')}</th>
                      <th role="button" onClick={() => handleSort('uploadedAt')}>Uploaded{sortIcon('uploadedAt')}</th>
                      <th>Version</th>
                      <th style={{ width: 120 }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {files.map((f, i) => (
                      <tr key={`${f.fileName}-${i}`}>
                        <td><i className="bi bi-file-earmark me-1 text-muted"></i>{f.fileName}</td>
                        {search && <td className="text-muted small">{f.folderName}</td>}
                        <td className="text-muted small">{formatSize(f.fileSize)}</td>
                        <td className="text-muted small">{formatDate(f.uploadedAt)}</td>
                        <td>
                          <button className="btn btn-link btn-sm p-0 text-decoration-none" style={{ color: '#2d6a4f' }} onClick={() => showVersions(f)}>
                            v{f.latestVersion}
                          </button>
                        </td>
                        <td>
                          {canDownload && (
                            <button className="btn btn-sm btn-outline-forest me-1" onClick={() => handleDownload(f)} title="Download">
                              <i className="bi bi-download"></i>
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                    {files.length === 0 && <tr><td colSpan={search ? 6 : 5} className="text-center text-muted py-4">No files found</td></tr>}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {!currentFolder && !search && childFolders.length === 0 && (
            <div className="text-center text-muted py-5">
              <i className="bi bi-folder-x" style={{ fontSize: 48 }}></i>
              <p className="mt-2">No folders available. {role === 'admin' ? 'Create folders in the Folders tab.' : 'Ask an admin to assign folders to you.'}</p>
            </div>
          )}
        </>
      )}

      {/* Version history modal */}
      {versions && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }} onClick={() => setVersions(null)}>
          <div className="modal-dialog modal-dialog-centered" onClick={e => e.stopPropagation()}>
            <div className="modal-content">
              <div className="modal-header" style={{ backgroundColor: '#2d6a4f', color: '#fff' }}>
                <h6 className="modal-title"><i className="bi bi-clock-history me-2"></i>Versions: {versionFile}</h6>
                <button className="btn-close btn-close-white" onClick={() => setVersions(null)}></button>
              </div>
              <div className="modal-body p-0">
                <table className="table table-hover mb-0">
                  <thead style={{ backgroundColor: '#e9f5ef' }}>
                    <tr><th>Version</th><th>Size</th><th>Uploaded By</th><th>Date</th>{canDownload && <th></th>}</tr>
                  </thead>
                  <tbody>
                    {versions.map(v => (
                      <tr key={v.versionNumber}>
                        <td>v{v.versionNumber}</td>
                        <td className="small text-muted">{formatSize(v.fileSize)}</td>
                        <td className="small text-muted">{v.uploadedBy}</td>
                        <td className="small text-muted">{formatDate(v.uploadedAt)}</td>
                        {canDownload && (
                          <td>
                            <button className="btn btn-sm btn-outline-forest" onClick={() => handleDownload({ fileName: versionFile, folderId: currentFolder?.folderId }, v.versionNumber)}>
                              <i className="bi bi-download"></i>
                            </button>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
