import React, { useState } from 'react';

// Icon Components
const MailIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" /></svg>
);
const LockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>
);
const EyeIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
);
const EyeOffIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>
);


// The Login/Registration Component
export const AuthForm = ({ onLoginSuccess }) => {
  const [isLoginView, setIsLoginView] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [apiMessage, setApiMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFormSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setApiMessage('');

    
    const endpoint = isLoginView ? '/api/v1/token' : '/api/v1/users/';
    
    const body = isLoginView 
      ? new URLSearchParams({ username: email, password: password })
      : JSON.stringify({ email, password });
    const headers = isLoginView
      ? { 'Content-Type': 'application/x-www-form-urlencoded' }
      : { 'Content-Type': 'application/json' };

    try {
      const response = await fetch(endpoint, { method: 'POST', headers, body });
      
      const text = await response.text();
      const data = text ? JSON.parse(text) : {};

      if (!response.ok) throw new Error(data.detail || 'An error occurred.');

      if (isLoginView) {
        onLoginSuccess(data.access_token, email);
      } else {
        setApiMessage(`Registration successful for ${data.email}! You can now log in.`);
        setIsLoginView(true);
      }
    } catch (error) {
      setApiMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md animate-fade-in">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-orange-500 tracking-wider">FirePulse+</h1>
        <p className="text-gray-400 mt-2">Your AI-Powered Entertainment Assistant</p>
      </div>
      <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl shadow-orange-500/10">
        <h2 className="text-3xl font-bold text-center text-white mb-2">
          {isLoginView ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p className="text-gray-400 text-center mb-8">
          {isLoginView ? 'Sign in to continue' : 'Get started with your free account'}
        </p>
        <form onSubmit={handleFormSubmit}>
          <div className="relative mb-4">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500"><MailIcon /></span>
            <input type="email" placeholder="Email Address" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500" required />
          </div>
          <div className="relative mb-6">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500"><LockIcon /></span>
            <input 
              type={showPassword ? 'text' : 'password'} 
              placeholder="Password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              className="w-full pl-10 pr-10 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500" required 
            />
            <button 
              type="button" 
              onClick={() => setShowPassword(!showPassword)} 
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-white"
            >
              {showPassword ? <EyeOffIcon /> : <EyeIcon />}
            </button>
          </div>
          <button type="submit" disabled={isLoading} className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 rounded-lg shadow-lg hover:shadow-orange-600/40 transition-all duration-300 disabled:bg-gray-500 flex items-center justify-center">
            {isLoading ? <div className="w-6 h-6 border-4 border-t-transparent border-white rounded-full animate-spin"></div> : (isLoginView ? 'Sign In' : 'Create Account')}
          </button>
        </form>
        {apiMessage && <div className="mt-4 text-center p-3 rounded-lg bg-gray-700/50 text-sm"><p>{apiMessage}</p></div>}
        <p className="text-center text-gray-400 mt-8">
          {isLoginView ? "Don't have an account?" : "Already have an account?"}
          <button onClick={() => { setIsLoginView(!isLoginView); setApiMessage(''); }} className="font-bold text-orange-500 hover:text-orange-400 ml-2 focus:outline-none">
            {isLoginView ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  );
};

