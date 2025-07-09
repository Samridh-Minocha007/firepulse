import React, { useState, useRef, useEffect } from 'react';

const VideoIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 18a2 2 0 0 1-2-2V8a2 0 0 1 2-2h.1a2 0 0 1 2 1.9v8.2a2 0 0 1-2.1 2Z"/><path d="m10 10-4 4 4 4"/><path d="m10 14H2"/></svg>
);

export const WatchParty = ({ authToken, userEmail }) => { // authToken is received but NOT used in WS URL
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [partyId, setPartyId] = useState('movie_night'); // Default party ID
    const [isConnected, setIsConnected] = useState(false);
    const websocket = useRef(null);
    const messagesEndRef = useRef(null);

    // Restore last used partyId from localStorage
    useEffect(() => {
        const savedPartyId = localStorage.getItem('partyId');
        if (savedPartyId) setPartyId(savedPartyId);
    }, []);

    // Scroll to bottom when chat updates
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Save partyId to localStorage on change
    useEffect(() => {
        if (partyId) localStorage.setItem('partyId', partyId);
    }, [partyId]);

    const connect = () => {
        // Prevent multiple connections
        if (websocket.current && websocket.current.readyState === WebSocket.OPEN) return;
        
        // Ensure partyId and userEmail are available before attempting to connect
        // Note: Backend expects userEmail in path, not authToken in query for this specific WS endpoint
        if (!partyId || !userEmail) {
            setMessages(prev => [...prev, { type: 'error', text: 'Error: Party ID and/or User Email missing. Please log in.' }]);
            return;
        }

        // UPDATED WebSocket URL to match backend's /ws/{party_id}/{user_id} path
        const ws_url = `ws://127.0.0.1:8000/api/v1/ws/${partyId}/${userEmail}`;
        
        websocket.current = new WebSocket(ws_url);

        websocket.current.onopen = () => {
            setIsConnected(true);
            setMessages(prev => [...prev, { type: 'status', text: `Connected to party '${partyId}' as ${userEmail}` }]);
        };

        websocket.current.onmessage = (event) => {
            setMessages(prev => [...prev, { type: 'message', text: event.data }]);
        };

        websocket.current.onclose = (event) => {
            setIsConnected(false);
            let reason = 'Disconnected.';
            if (event.reason) {
                reason = `Disconnected: ${event.reason} (Code: ${event.code})`;
            }
            setMessages(prev => [...prev, { type: 'status', text: reason }]);
            websocket.current = null;
        };

        websocket.current.onerror = (error) => {
            console.error("WebSocket error:", error);
            setMessages(prev => [...prev, { type: 'error', text: 'Connection error. Check console for details.' }]);
            setIsConnected(false); // Ensure isConnected is false on error
            websocket.current = null;
        };
    };
    
    const disconnect = () => {
        if (websocket.current) {
            websocket.current.close(1000, "User initiated disconnect"); // 1000 is normal closure
        }
    };

    const sendMessage = () => {
        if (input.trim() === '') return; // Don't send empty messages

        if (websocket.current?.readyState === WebSocket.OPEN) {
            websocket.current.send(input);
            setInput('');
        } else {
            setMessages(prev => [...prev, { type: 'error', text: 'Error: Not connected to watch party.' }]);
        }
    };
    
    const handleStartVideoCall = () => {
        const meetUrl = `https://meet.jit.si/firepulse-${partyId}`;
        window.open(meetUrl, '_blank');
        const announcement = `${userEmail} has started a video call! Join here: ${meetUrl}`;
        if (websocket.current?.readyState === WebSocket.OPEN) {
            websocket.current.send(announcement);
        } else {
            setMessages(prev => [...prev, { type: 'error', text: 'Error: Not connected to watch party to announce video call.' }]);
        }
    };

    const handleSuggestMovie = () => {
        if (websocket.current?.readyState === WebSocket.OPEN) {
            websocket.current.send('suggest_movie'); // Backend should handle this message
        } else {
            setMessages(prev => [...prev, { type: 'error', text: 'Error: Not connected to watch party to suggest movie.' }]);
        }
    };

    const renderMessage = (msg) => {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const parts = msg.text.split(urlRegex);
        return parts.map((part, index) => {
            if (part.match(urlRegex)) {
                return <a key={index} href={part} target="_blank" rel="noopener noreferrer" className="text-blue-400 underline hover:text-blue-300">{part}</a>;
            }
            return part;
        });
    };

    return (
        <div className="w-full p-8 animate-fade-in">
            <h2 className="text-4xl font-bold text-white mb-8">Watch Party</h2>
            <div className="bg-gray-800 p-8 rounded-2xl shadow-lg">
                {!isConnected ? (
                    <div className="text-center">
                        <h3 className="text-2xl text-white font-semibold mb-4">Join a Party</h3>
                        <div className="flex justify-center items-center gap-4">
                            <input 
                                type="text" 
                                value={partyId} 
                                onChange={(e) => setPartyId(e.target.value)} 
                                placeholder="Enter Party ID" 
                                className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                            />
                            <button 
                                onClick={connect} 
                                className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-lg disabled:opacity-50"
                                disabled={!partyId || !userEmail} // Disable if partyId or userEmail is missing
                            >
                                Connect
                            </button>
                        </div>
                        {!userEmail && <p className="text-red-400 mt-2">Please log in to use Watch Party (user email required).</p>}
                    </div>
                ) : (
                    <div className="flex flex-col h-[75vh]">
                        <div className="flex justify-between items-center mb-4">
                            <div className="flex gap-4">
                                <button onClick={handleSuggestMovie} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg">Suggest a Movie!</button>
                                <button onClick={handleStartVideoCall} className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg flex items-center gap-2"><VideoIcon /> Start Video Call</button>
                            </div>
                            <button onClick={disconnect} className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg">Disconnect</button>
                        </div>
                        <div className="flex-grow bg-gray-900/50 rounded-lg p-4 overflow-y-auto">
                            {messages.map((msg, index) => (
                                <p key={index} className={`mb-2 ${msg.type === 'status' ? 'text-gray-500 italic' : msg.type === 'error' ? 'text-red-400' : 'text-white'}`}>
                                    {renderMessage(msg)}
                                </p>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>
                        <div className="mt-4 flex gap-4">
                            <input 
                                type="text" 
                                value={input} 
                                onChange={(e) => setInput(e.target.value)} 
                                onKeyPress={(e) => e.key === 'Enter' && sendMessage()} 
                                placeholder="Type a message..." 
                                className="flex-grow bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            />
                            <button onClick={sendMessage} className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-2 px-6 rounded-lg">Send</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
