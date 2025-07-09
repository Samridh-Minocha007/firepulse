import React, { useState, useEffect } from 'react';
import { useTypewriter } from '../hooks/useTypewriter'; 

export const Dashboard = ({ authToken }) => {
    const [query, setQuery] = useState('');
    const [searchType, setSearchType] = useState('movie');
    const [isLoading, setIsLoading] = useState(false);
    const [resultText, setResultText] = useState('');
    const [error, setError] = useState('');
    
    // State for time-based recommendations
    const [timeBasedRecommendations, setTimeBasedRecommendations] = useState([]);
    const [isLoadingTimeRecs, setIsLoadingTimeRecs] = useState(true);
    const [timeRecsError, setTimeRecsError] = useState('');
    const [timeRecsGreeting, setTimeRecsGreeting] = useState(''); 

    const typedResult = useTypewriter(resultText, 30);

    
    useEffect(() => {
        const fetchTimeBasedRecommendations = async () => {
            console.log("DEBUG: fetchTimeBasedRecommendations called. authToken:", authToken); 
            if (!authToken) {
                setIsLoadingTimeRecs(false);
                setTimeRecsError('Authentication required for time-based recommendations.');
                console.log("DEBUG: No authToken, skipping fetch."); 
                return;
            }
            setIsLoadingTimeRecs(true);
            setTimeRecsError('');
            setTimeRecsGreeting(''); 
            try {
                const hour = new Date().getHours();
                let timeOfDay;
                if (hour >= 5 && hour < 12) {
                    timeOfDay = 'morning';
                } else if (hour >= 12 && hour < 17) {
                    timeOfDay = 'afternoon';
                } else if (hour >= 17 && hour < 21) {
                    timeOfDay = 'evening';
                } else {
                    timeOfDay = 'night';
                }

                
                const response = await fetch(`/api/v1/time-based-suggestions?time_of_day=${timeOfDay}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` },
                });
                
                console.log("DEBUG: Time recs fetch response status:", response.status);
                const data = await response.json();
                console.log("DEBUG: Time recs fetch response data:", data); 

                if (!response.ok) {
                    throw new Error(data.detail || 'Could not fetch time-based recommendations.');
                }
                setTimeBasedRecommendations(data.suggestions || []); 
                setTimeRecsGreeting(data.greeting || "Here are some recommendations for you!"); 
                console.log("DEBUG: Time recs set to state:", data.suggestions); 
            } catch (err) {
                console.error("DEBUG: Failed to fetch time-based suggestion:", err); 
                setTimeRecsError(err.message);
            } finally {
                setIsLoadingTimeRecs(false);
            }
        };
        fetchTimeBasedRecommendations();
    }, [authToken]); 

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query) return;
        setIsLoading(true);
        setResultText('');
        setError('');
        const endpoint = searchType === 'movie' ? '/api/v1/movies' : '/api/v1/songs';
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
                body: JSON.stringify({ query: query }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'An error occurred.');
            setResultText(data.text || 'I found some results for you!');
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full p-8 animate-fade-in">
            <h2 className="text-4xl font-bold text-white mb-4">Meet Alex,</h2>
            <p className="text-xl text-gray-400 mb-8">your personal entertainment guide. What can I help you find today?</p>
            
            {/* Original Search/Chatbot Section (moved to top) */}
            <div className="bg-gray-800 p-8 rounded-2xl shadow-lg mb-8">
                <form onSubmit={handleSearch}>
                    <div className="flex items-center gap-4 mb-4">
                        <input 
                            type="text" 
                            value={query} 
                            onChange={(e) => setQuery(e.target.value)} 
                            placeholder={`e.g., "sad movies" or "songs by Taylor Swift"`} 
                            className="flex-grow bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                        />
                        <div className="flex bg-gray-700 p-1 rounded-lg">
                            <button 
                                type="button" 
                                onClick={() => setSearchType('movie')} 
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${searchType === 'movie' ? 'bg-orange-600 text-white' : 'text-gray-300 hover:bg-gray-600'}`}
                            >
                                Movies
                            </button>
                            <button 
                                type="button" 
                                onClick={() => setSearchType('song')} 
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${searchType === 'song' ? 'bg-orange-600 text-white' : 'text-gray-300 hover:bg-gray-600'}`}
                            >
                                Songs
                            </button>
                        </div>
                        <button type="submit" disabled={isLoading} className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-lg disabled:bg-gray-500">
                            {isLoading ? 'Asking...' : 'Ask Alex'}
                        </button>
                    </div>
                </form>
                <div className="mt-6 min-h-[200px] bg-gray-900/50 p-6 rounded-lg font-mono text-lg">
                    {isLoading && <p className="text-gray-400">Alex is thinking...</p>}
                    {error && !isLoading && <p className="text-red-400">{error}</p>}
                    {!isLoading && !error && (
                        <p className="text-white whitespace-pre-wrap">
                            {typedResult}
                            {resultText && typedResult === resultText ? '' : <span className="animate-pulse">|</span>}
                        </p>
                    )}
                </div>
            </div>

            {/* Time-Based Recommendations Section (moved below chat) */}
            <div className="bg-gray-800 p-8 rounded-2xl shadow-lg mb-8">
                <h3 className="text-2xl text-white font-semibold mb-4">
                    {timeRecsGreeting || "Recommendations for This Time of Day"} {/* Display the greeting here */}
                </h3>
                {isLoadingTimeRecs && <p>Loading time-based recommendations...</p>}
                {timeRecsError && <p className="text-red-400">{timeRecsError}</p>}
                {!isLoadingTimeRecs && !timeRecsError && (
                    <ul>
                        {timeBasedRecommendations.length > 0 ? (
                            timeBasedRecommendations.map((item, index) => (
                                <li key={item.id || index} className="border-b border-gray-700 py-2 text-gray-300">
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
                            <p>No time-based recommendations available right now.</p>
                        )}
                    </ul>
                )}
            </div>
        </div>
    );
};
