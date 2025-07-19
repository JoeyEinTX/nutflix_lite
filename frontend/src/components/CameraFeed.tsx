import React, { useState, useEffect, useRef } from 'react';

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
  const [streamError, setStreamError] = useState(false);
  const [imageKey, setImageKey] = useState(0);
  const [useMjpeg, setUseMjpeg] = useState(true);
  const imgRef = useRef<HTMLImageElement>(null);

  // Detect mobile or slow connections for better UX
  const shouldUseMjpeg = () => {
    const userAgent = navigator.userAgent.toLowerCase();
    const isMobile = /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/.test(userAgent);
    
    // Check network connection if available
    const connection = (navigator as any).connection;
    const isSlowConnection = connection && (
      connection.effectiveType === 'slow-2g' || 
      connection.effectiveType === '2g' ||
      connection.saveData
    );
    
    // Use snapshots for mobile or slow connections to save bandwidth
    return !isMobile && !isSlowConnection;
  };

  // Initialize stream preference based on device/connection
  useEffect(() => {
    setUseMjpeg(shouldUseMjpeg());
  }, []);

  // Refresh snapshots every 2 seconds when using snapshot mode
  useEffect(() => {
    if (!useMjpeg) {
      const interval = setInterval(() => {
        setImageKey(prev => prev + 1);
        setImageError(false); // Reset error state on refresh
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [useMjpeg]);

  const handleStreamError = () => {
    console.log(`MJPEG stream failed for ${title}, falling back to snapshots`);
    setStreamError(true);
    setUseMjpeg(false);
  };

  const handleImageError = () => {
    setImageError(true);
    // Retry after 2 seconds
    setTimeout(() => {
      setImageError(false);
      setImageKey(prev => prev + 1);
    }, 2000);
  };

  const handleImageLoad = () => {
    setImageError(false);
    setStreamError(false);
  };

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onFullscreen();
  };

  // Determine which source to use
  const currentSource = useMjpeg && !streamError ? streamUrl : `${snapshotUrl}?t=${imageKey}`;
  const feedMode = useMjpeg && !streamError ? 'live stream' : 'live preview';

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
              ref={imgRef}
              src={currentSource}
              alt={`${title} Feed`}
              className="w-full aspect-video object-cover border border-stone-600 rounded transition-transform group-hover:scale-105"
              onError={useMjpeg ? handleStreamError : handleImageError}
              onLoad={handleImageLoad}
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
          {feedMode} • Click for full stream
          {streamError && <span className="text-amber-400"> (using snapshots)</span>}
        </div>
      </div>
    </div>
  );
}
