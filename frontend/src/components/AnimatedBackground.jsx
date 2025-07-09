import React from 'react';

export const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 z-0">
      <div className="absolute inset-0 bg-gray-900"></div>
      <div className="absolute inset-0 bg-gradient-to-r from-orange-900/50 via-black to-blue-900/50 animate-gradient-xy"></div>
    </div>
  );
};