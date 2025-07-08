import React from 'react';

// This is the screen the user will see after logging in.
// It receives the user's email and a logout function as "props".
export const Dashboard = ({ userEmail, onLogout }) => {
  return (
    <div className="w-full max-w-4xl mx-auto p-4 animate-fade-in">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-orange-500">FirePulse+</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-300">Welcome, {userEmail}</span>
          <button 
            onClick={onLogout}
            className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </header>
      
      <main className="bg-gray-800 p-8 rounded-2xl shadow-lg">
        <h2 className="text-2xl text-white font-semibold mb-4">Your Dashboard</h2>
        <p className="text-gray-400">
          This is where your personalized movie and music recommendations will appear. 
          We will build out this section next!
        </p>
      </main>
    </div>
  );
};
