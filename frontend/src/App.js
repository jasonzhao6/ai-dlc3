import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AppLayout from './components/AppLayout';
import LoginPage from './pages/LoginPage';
import FileBrowserPage from './pages/FileBrowserPage';
import UserManagementPage from './pages/UserManagementPage';
import FolderManagementPage from './pages/FolderManagementPage';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './App.css';

function ProtectedRoute({ children, adminOnly }) {
  const { session } = useAuth();
  if (!session) return <Navigate to="/login" />;
  if (adminOnly && session.role !== 'admin') return <Navigate to="/" />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route index element={<FileBrowserPage />} />
            <Route path="users" element={<ProtectedRoute adminOnly><UserManagementPage /></ProtectedRoute>} />
            <Route path="folders" element={<ProtectedRoute adminOnly><FolderManagementPage /></ProtectedRoute>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
