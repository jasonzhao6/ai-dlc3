import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const token = sessionStorage.getItem('sessionToken');
    const username = sessionStorage.getItem('username');
    const role = sessionStorage.getItem('role');
    const mustChangePassword = sessionStorage.getItem('mustChangePassword') === 'true';
    return token ? { token, username, role, mustChangePassword } : null;
  });

  const login = (data) => {
    sessionStorage.setItem('sessionToken', data.sessionToken);
    sessionStorage.setItem('username', data.username);
    sessionStorage.setItem('role', data.role);
    sessionStorage.setItem('mustChangePassword', data.mustChangePassword);
    setSession({ token: data.sessionToken, username: data.username, role: data.role, mustChangePassword: data.mustChangePassword });
  };

  const logout = () => {
    sessionStorage.clear();
    setSession(null);
  };

  const clearMustChangePassword = () => {
    sessionStorage.setItem('mustChangePassword', 'false');
    setSession(prev => ({ ...prev, mustChangePassword: false }));
  };

  return (
    <AuthContext.Provider value={{ session, login, logout, clearMustChangePassword }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
