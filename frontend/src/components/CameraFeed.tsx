import React, { useState } from 'react';

interface CameraFeedProps {
  id: string;
  title: string;
  location: string;
  streamUrl: string;
  snapshotUrl: string;
  onFullscreen: () => void;
}

export function CameraFeed({ id, title, location, streamUrl, snapshotUrl, onFullscreen }: CameraFeedProps) {
  const [imageError, setImageError] = useState(false);
  const [imageKey, setImageKey] = useState(0);

  // Refresh image every 2 seconds for live preview
  React.useEffect(() => {
    const interval = setInterval(() => {
      setImageKey(prev => prev + 1);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleImageError = () => {
    setImageError(true);
    // Retry after 2 seconds
    setTimeout(() => {
      setImageError(false);
      setImageKey(prev => prev + 1);
    }, 2000);
  };

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onFullscreen();
  };

  return (
    <div className="camera-feed-container">
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-medium text-amber-200">{title}</h3>
            <p className="text-sm text-stone-400">{location}</p>
          </div>
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
        </div>
        
        <div 
          className="relative cursor-pointer group"
          onClick={handleClick}
          title="Click for fullscreen view"
        >
          {imageError ? (
            <div className="w-full aspect-video bg-stone-800 border border-stone-600 rounded flex items-center justify-center">
              <div className="text-center text-stone-400">
                <div className="text-2xl mb-2">📷</div>
                <p className="text-sm">Camera connecting...</p>
                <p className="text-xs">Retrying in 2 seconds</p>
              </div>
            </div>
          ) : (
            <img
              src={`${snapshotUrl}?t=${imageKey}`}
              alt={`${title} Feed`}
              className="w-full aspect-video object-cover border border-stone-600 rounded transition-transform group-hover:scale-105"
              onError={handleImageError}
            />
          )}
          
          {/* Overlay for fullscreen hint */}
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors rounded flex items-center justify-center">
            <div className="opacity-0 group-hover:opacity-100 transition-opacity text-white text-sm bg-black/50 px-3 py-1 rounded">
              Click for live stream
            </div>
          </div>
        </div>
        
        <div className="mt-3 text-xs text-stone-500 text-center">
          Live preview • Click for full stream
        </div>
      </div>
    </div>
  );
}
