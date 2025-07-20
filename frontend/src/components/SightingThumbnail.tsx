import React from 'react';

interface SightingThumbnailProps {
  id: string;
  animal: string;
  location: string;
  timestamp: string;
  image: string;
  onClick: () => void;
}

export function SightingThumbnail({ animal, location, timestamp, image, onClick }: SightingThumbnailProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const today = new Date();
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    }
    
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    }
    
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  return (
    <div 
      className="bg-stone-900/50 border border-stone-700 rounded-lg overflow-hidden cursor-pointer hover:border-amber-500 transition-colors"
      onClick={onClick}
    >
      <div className="aspect-video relative">
        <img
          src={image}
          alt={animal}
          className="w-full h-full object-cover"
        />
      </div>
      
      <div className="p-3">
        <h4 className="text-sm font-medium text-amber-200 mb-1">{animal}</h4>
        <p className="text-xs text-stone-400 mb-2">{location}</p>
        <div className="flex items-center justify-between text-xs text-stone-500">
          <span>{formatDate(timestamp)}</span>
          <span>{formatTime(timestamp)}</span>
        </div>
      </div>
    </div>
  );
}
