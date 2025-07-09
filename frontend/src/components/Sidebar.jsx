import React from 'react';

const SidebarIcon = ({ children }) => <span className="mr-3">{children}</span>;

export const Sidebar = ({ onLogout, userEmail, activeView, setActiveView }) => {
  const menuItems = [
    { name: 'Discover', icon: '🔍' },
    { name: 'My History', icon: '📜' },
    { name: 'Trivia Game', icon: '❓' },
    { name: 'Calendar', icon: '🗓️' },
    { name: 'Watch Party', icon: '🎉' },
  ];

  
  const handleItemClick = (viewName) => {
    console.log(`[Sidebar.jsx] Clicked on: ${viewName}. Setting active view.`);
    setActiveView(viewName);
  };

  return (
    <div className="w-64 bg-gray-900 h-screen p-5 flex flex-col shadow-2xl">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-orange-500">FirePulse+</h1>
        <p className="text-sm text-gray-500">Welcome, {userEmail}</p>
      </div>
      <nav className="flex-grow">
        <ul>
          {menuItems.map(item => (
            <li key={item.name} className="mb-4">
              <button
                onClick={() => handleItemClick(item.name)}
                className={`w-full flex items-center p-3 text-gray-300 rounded-lg hover:bg-orange-600 hover:text-white transition-colors duration-200 text-left
                  ${activeView === item.name ? 'bg-orange-600 text-white' : ''}
                `}
              >
                <SidebarIcon>{item.icon}</SidebarIcon>
                {item.name}
              </button>
            </li>
          ))}
        </ul>
      </nav>
      <div>
        <button onClick={onLogout} className="w-full p-3 text-gray-300 rounded-lg hover:bg-red-600 hover:text-white transition-colors duration-200 flex items-center">
          <SidebarIcon>🚪</SidebarIcon>
          Logout
        </button>
      </div>
    </div>
  );
};
