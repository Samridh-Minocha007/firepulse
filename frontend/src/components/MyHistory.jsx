import React, { useState, useEffect } from 'react';

export const MyHistory = ({ authToken }) => {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [movieInput, setMovieInput] = useState(''); 
  const [isLogging, setIsLogging] = useState(false); 
  const [logMessage, setLogMessage] = useState(''); 

  const fetchHistory = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch('/api/v1/history/recommendations', {
        headers: { 'Authorization': `Bearer ${authToken}` },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not fetch history.');
      setHistory(data.suggestions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogMovie = async () => {
    if (!movieInput.trim() || !authToken) {
      setLogMessage('Please enter a movie title and ensure you are logged in.');
      return;
    }

    setIsLogging(true);
    setLogMessage('');
    try {
      const response = await fetch('/api/v1/history/log-watch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({ movie_name: movieInput }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to log movie.');
      setLogMessage(data.message);
      setMovieInput(''); 
      fetchHistory(); 
    } catch (err) {
      setLogMessage(`Error logging movie: ${err.message}`);
    } finally {
      setIsLogging(false);
    }
  };

  useEffect(() => {
    if (authToken) {
      fetchHistory();
    }
  }, [authToken]);

  return (
    <div className="w-full p-8 animate-fade-in">
      <h2 className="text-4xl font-bold text-white mb-8">My Watch History</h2>
      <div className="bg-gray-800 p-8 rounded-2xl shadow-lg mb-6">
        <h3 className="text-2xl text-white font-semibold mb-4">Log a Watched Movie</h3>
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            value={movieInput}
            onChange={(e) => setMovieInput(e.target.value)}
            placeholder="Enter movie title"
            className="flex-grow bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          <button
            onClick={handleLogMovie}
            disabled={isLogging || !movieInput.trim()}
            className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-lg disabled:bg-gray-500"
          >
            {isLogging ? 'Logging...' : 'Log Movie'}
          </button>
        </div>
        {logMessage && <p className="text-sm text-gray-400">{logMessage}</p>}
      </div>

      <div className="bg-gray-800 p-8 rounded-2xl shadow-lg">
        <h3 className="text-2xl text-white font-semibold mb-4">Recommendations Based on History</h3>
        {isLoading && <p>Loading history and recommendations...</p>}
        {error && <p className="text-red-400">{error}</p>}
        {!isLoading && !error && (
          <ul>
            {history.length > 0 ? (
              history.map((item, index) => (
                <li key={item.id || index} className="border-b border-gray-700 py-2 text-gray-300">
                  {/* Make movie title a hyperlink */}
                  <a 
                    href={`https://www.google.com/search?q=${encodeURIComponent(item.title || 'Unknown Movie')}+movie`} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-blue-400 hover:text-blue-300 underline"
                  >
                    {item.title || 'Unknown Title'}
                  </a>
                </li>
              ))
            ) : (
              <p>You haven't logged any movies yet. Your recommendations based on history will appear here.</p>
            )}
          </ul>
        )}
      </div>
    </div>
  );
};
