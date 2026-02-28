const API_BASE = process.env.REACT_APP_API_URL || '';

async function request(path, options = {}) {
  const token = sessionStorage.getItem('sessionToken');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (res.status === 401) {
    sessionStorage.clear();
    window.location.href = '/login';
    return;
  }

  if (!res.ok) throw new Error(data.error || `Request failed: ${res.status}`);
  return data;
}

export const api = {
  // Auth
  login: (username, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  changePassword: (currentPassword, newPassword) => request('/auth/change-password', { method: 'POST', body: JSON.stringify({ currentPassword, newPassword }) }),
  seedAdmin: () => request('/auth/seed-admin', { method: 'POST' }),

  // Users
  getUsers: () => request('/users'),
  createUser: (data) => request('/users', { method: 'POST', body: JSON.stringify(data) }),
  updateUser: (username, data) => request(`/users/${username}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteUser: (username) => request(`/users/${username}`, { method: 'DELETE' }),

  // Folders
  getFolders: () => request('/folders'),
  createFolder: (data) => request('/folders', { method: 'POST', body: JSON.stringify(data) }),
  deleteFolder: (folderId) => request(`/folders/${folderId}`, { method: 'DELETE' }),
  assignFolders: (data) => request('/folders/assignments', { method: 'POST', body: JSON.stringify(data) }),
  unassignFolders: (data) => request('/folders/assignments', { method: 'DELETE', body: JSON.stringify(data) }),

  // Files
  getFiles: (params) => request(`/files?${new URLSearchParams(params)}`),
  getVersions: (folderId, fileName) => request(`/files/${folderId}/${encodeURIComponent(fileName)}/versions`),
  getUploadUrl: (data) => request('/files/upload-url', { method: 'POST', body: JSON.stringify(data) }),
  getDownloadUrl: (data) => request('/files/download-url', { method: 'POST', body: JSON.stringify(data) }),
};
