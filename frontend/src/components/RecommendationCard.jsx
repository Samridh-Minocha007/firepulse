import React from 'react';

// A new, reusable component to display a single movie or song recommendation.
// It takes an 'item' object (our mock data) and a 'type' as props.
export const RecommendationCard = ({ item, type }) => {
  // Determine the image, title, and subtitle based on the type of item.
  const imageUrl = type === 'movie' ? item.poster_url : item.album_url;
  const title = item.title;
  const subtitle = type === 'movie' ? (item.overview || '').substring(0, 70) + '...' : item.artist;

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden transform hover:-translate-y-2 transition-transform duration-300 shadow-lg hover:shadow-orange-500/20">
      <img 
        // Use a placeholder if no image is available.
        src={imageUrl || 'https://placehold.co/500x750/1f2937/a9a9a9?text=No+Image'} 
        alt={title} 
        className="w-full h-64 object-cover"
      />
      <div className="p-4">
        <h3 className="font-bold text-lg text-white truncate" title={title}>{title}</h3>
        <p className="text-sm text-gray-400 mt-1 h-10">{subtitle}</p>
      </div>
    </div>
  );
};