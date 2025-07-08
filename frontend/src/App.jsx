import React, { useState, useEffect } from 'react';
import { AuthForm } from './components/AuthForm';
import { Dashboard } from './components/Dashboard';

// This is our main application component. It acts as a controller.
export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(null);
  const [userEmail, setUserEmail] = useState('');

  // --- NEW: Check for a token when the app first loads ---
  // `useEffect` is a hook that runs code after the component renders.
  // An empty dependency array `[]` means it only runs once, like componentDidMount.
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const email = localStorage.getItem('userEmail');
    if (token && email) {
      setAuthToken(token);
      setUserEmail(email);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (token, email) => {
    // Save token and email to localStorage for persistence
    localStorage.setItem('authToken', token);
    localStorage.setItem('userEmail', email);
    setAuthToken(token);
    setUserEmail(email);
    setIsAuthenticated(true);
  };
  
  const handleLogout = () => {
    // Clear token and email from localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setAuthToken(null);
    setUserEmail('');
    setIsAuthenticated(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center font-sans p-4">
      {isAuthenticated ? (
        <Dashboard userEmail={userEmail} onLogout={handleLogout} />
      ) : (
        <AuthForm onLoginSuccess={handleLogin} />
      )}
    </div>
  );
}
