import React, { useState, useEffect } from 'react';

export const TriviaGame = ({ authToken }) => {
  const [topic, setTopic] = useState('Movies');
  const [question, setQuestion] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [userBadges, setUserBadges] = useState([]); // New state for user badges
  const [totalPoints, setTotalPoints] = useState(0); // New state for total points
  const [isFetchingUserData, setIsFetchingUserData] = useState(true); // New state for user data loading

  // Function to fetch user badges and points
  const fetchUserData = async () => {
    if (!authToken) return;
    setIsFetchingUserData(true);
    try {
      // Fetch Badges
      const badgesResponse = await fetch('/api/v1/users/me/badges', {
        headers: { 'Authorization': `Bearer ${authToken}` },
      });
      const badgesData = await badgesResponse.json();
      if (!badgesResponse.ok) throw new Error(badgesData.detail || 'Failed to fetch badges.');
      setUserBadges(badgesData);

      // Fetch Total Points (assuming a new endpoint for this, e.g., /api/v1/users/me/points)
      // You'll need to implement this backend endpoint.
      const pointsResponse = await fetch('/api/v1/users/me/points', {
        headers: { 'Authorization': `Bearer ${authToken}` },
      });
      const pointsData = await pointsResponse.json();
      if (!pointsResponse.ok) throw new Error(pointsData.detail || 'Failed to fetch points.');
      setTotalPoints(pointsData.total_points || 0);

    } catch (error) {
      console.error("Error fetching user data:", error);
      // setFeedback(`Error fetching user data: ${error.message}`); // Optional: show error to user
    } finally {
      setIsFetchingUserData(false);
    }
  };

  useEffect(() => {
    fetchUserData(); // Fetch user data on component mount or authToken change
  }, [authToken]);

  const handleStartGame = async () => {
    if (!authToken) return;

    setIsLoading(true);
    setFeedback('');
    setQuestion(null);

    try {
      const response = await fetch('/api/v1/trivia/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({ topic }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to start game.');
      setQuestion(data);
    } catch (error) {
      setFeedback(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerSubmit = async (answerText) => {
    if (!question || !authToken) return;

    setIsLoading(true);
    setFeedback('');

    try {
      const response = await fetch('/api/v1/trivia/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          question_id: question.id,
          selected_answer_text: answerText,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to submit answer.');
      setFeedback(data.message);
      setQuestion(null);
      fetchUserData(); // Refresh badges and points after submitting an answer
    } catch (error) {
      setFeedback(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full p-8 animate-fade-in">
      <h2 className="text-4xl font-bold text-white mb-8">Trivia Challenge</h2>
      <div className="bg-gray-800 p-8 rounded-2xl shadow-lg mb-6">
        {isFetchingUserData ? (
          <p>Loading user data...</p>
        ) : (
          <div className="flex justify-between items-center mb-4 text-white">
            <p className="text-xl font-semibold">Total Points: <span className="text-orange-400">{totalPoints}</span></p>
            <div>
              <p className="text-lg font-semibold mb-2">Badges:</p>
              {userBadges.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {userBadges.map(badge => (
                    <span key={badge.id} className="bg-blue-600 text-white text-xs font-semibold px-2.5 py-0.5 rounded-full">
                      {badge.name}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">No badges earned yet.</p>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="bg-gray-800 p-8 rounded-2xl shadow-lg">
        {!question && !feedback ? (
          <div className="text-center">
            <h3 className="text-2xl text-white font-semibold mb-4">Choose a Topic to Begin</h3>
            <div className="flex justify-center items-center gap-4">
              <input type="text" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g., Star Wars" className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-orange-500" />
              <button onClick={handleStartGame} disabled={isLoading} className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-lg disabled:bg-gray-500">
                {isLoading ? 'Generating...' : 'Start Game'}
              </button>
            </div>
          </div>
        ) : (
          <>
            {question && (
              <div>
                <p className="text-gray-400 text-lg mb-4">Category: {question.category}</p>
                <h3 className="text-2xl text-white font-semibold mb-6">{question.question_text}</h3>
                <div className="grid grid-cols-2 gap-4">
                  {question.answers.map((answer, index) => (
                    <button key={index} onClick={() => handleAnswerSubmit(answer.text)} disabled={isLoading} className="w-full p-4 bg-gray-700 rounded-lg text-left hover:bg-orange-600 transition-colors disabled:opacity-50">
                      {answer.text}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {feedback && (
              <div className="mt-6 p-4 bg-gray-900/50 rounded-lg text-center">
                <p>{feedback}</p>
                <button onClick={() => setFeedback('')} className="mt-4 bg-orange-600 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded-lg">
                  Play Again
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
