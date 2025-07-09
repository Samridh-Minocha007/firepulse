import React, { useState, useEffect } from 'react';
import { AuthForm } from './components/AuthForm';
import { Dashboard } from './components/Dashboard';
import { Sidebar } from './components/Sidebar';
import { TriviaGame } from './components/TriviaGame';
import { MyHistory } from './components/MyHistory';
import { CalendarEvents } from './components/CalendarEvents';
import { AnimatedBackground } from './components/AnimatedBackground';
import { WatchParty } from './components/WatchParty';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(null);
  const [userEmail, setUserEmail] = useState('');
  const [activeView, setActiveView] = useState('Discover');

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
    localStorage.setItem('authToken', token);
    localStorage.setItem('userEmail', email);
    setAuthToken(token);
    setUserEmail(email);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setAuthToken(null);
    setUserEmail('');
    setIsAuthenticated(false);
  };

  const renderActiveView = () => {
    switch (activeView) {
      case 'Discover':
        return <Dashboard authToken={authToken} />;
      case 'Trivia Game':
        return <TriviaGame authToken={authToken} />;
      case 'My History':
        return <MyHistory authToken={authToken} />;
      case 'Calendar':
        return <CalendarEvents authToken={authToken} />;
      case 'Watch Party':
        return <WatchParty userEmail={userEmail} />;
      default:
        return <Dashboard authToken={authToken} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-800 text-white font-sans relative">
      <AnimatedBackground />
      <div className="relative z-10">
        {isAuthenticated && authToken ? (
          <div className="flex">
            <Sidebar
              userEmail={userEmail}
              onLogout={handleLogout}
              activeView={activeView}
              setActiveView={setActiveView}
            />
            <main className="flex-grow">
              {renderActiveView()}
            </main>
          </div>
        ) : (
          <div className="flex items-center justify-center min-h-screen">
            <AuthForm onLoginSuccess={handleLogin} />
          </div>
        )}
      </div>
    </div>
  );
}
