import React, { useState, useEffect } from 'react';

export const CalendarEvents = ({ authToken }) => {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authToken) return;

    const fetchEvents = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await fetch('/api/v1/calendar/events/', {
          headers: { 'Authorization': `Bearer ${authToken}` },
        });
        const data = await response.json();
        
        setEvents(data.items || data || []); 
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, [authToken]);

  
  const energeticComedyMovies = [
    { title: "The Hangover", link: "https://www.google.com/search?q=The+Hangover+movie" },
    { title: "Guardians of the Galaxy", link: "https://www.google.com/search?q=Guardians+of+the+Galaxy+movie" },
    { title: "Deadpool", link: "https://www.google.com/search?q=Deadpool+movie" },
    { title: "21 Jump Street", link: "https://www.google.com/search?q=21+Jump+Street+movie" },
    { title: "Ferris Bueller's Day Off", link: "https://www.google.com/search?q=Ferris+Bueller%27s+Day+Off+movie" },
    { title: "Hera Pheri", link: "https://www.google.com/search?q=Hera+Pheri+movie" },
    { title: "3 Idiots", link: "https://www.google.com/search?q=3+Idiots+movie" },
    { title: "Dil Chahta Hai", link: "https://www.google.com/search?q=Dil+Chahta+Hai+movie" },
    { title: "Bhool Bhulaiyaa", link: "https://www.google.com/search?q=Bhool+Bhulaiyaa+movie" },
    { title: "Welcome", link: "https://www.google.com/search?q=Welcome+movie" },
  ];

  return (
    <div className="w-full p-8 animate-fade-in">
      <h2 className="text-4xl font-bold text-white mb-8">Upcoming Events</h2>
      <div className="bg-gray-800 p-8 rounded-2xl shadow-lg">
        {isLoading && <p>Loading events...</p>}
        {error && <p className="text-red-400">{error}</p>}
        {!isLoading && !error && (
          <ul>
            {Array.isArray(events) && events.length > 0 ? (
              events.map((event, index) => (
                <li key={index} className="border-b border-gray-700 py-3">
                  <p className="font-semibold text-white">{event.summary}</p>
                  <p className="text-sm text-gray-400">{new Date(event.start).toLocaleString()}</p>
                  {event.summary && event.summary.toLowerCase().includes('party') && (
                    <div className="mt-2">
                      <p className="text-orange-400 text-sm font-semibold">Looks like a party! Here are some energetic/comedy movies:</p>
                      <ul className="list-disc list-inside text-gray-300 text-sm ml-4">
                        {energeticComedyMovies.map((movie, movieIndex) => (
                          <li key={movieIndex}>
                            <a 
                              href={movie.link} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="text-blue-400 hover:text-blue-300 underline"
                            >
                              {movie.title}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </li>
              ))
            ) : (
              <p>No upcoming events found. Link your Google Account via the API docs to see events here.</p>
            )}
          </ul>
        )}
      </div>
    </div>
  );
};
