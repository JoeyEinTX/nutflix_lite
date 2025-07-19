import React, { useState, useEffect, useRef } from 'react';
// import { Maximize2 } from 'lucide-react';
// import { Button } from './ui/button';

interface CameraFeedProps {
  id: string;
  title: string;
  location: string;
  streamUrl: string;
  snapshotUrl: string;
  onFullscreen: () => void;
}

export function CameraFeed({ title, location, streamUrl, snapshotUrl, onFullscreen }: CameraFeedProps) {
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
    <div className="relative bg-card rounded-xl overflow-hidden border border-border shadow-lg hover:shadow-xl transition-shadow">
      <div className="aspect-video bg-gradient-to-br from-muted/50 to-muted relative">
        {imageError ? (
          <div className="absolute inset-0 flex items-center justify-center bg-muted">
            <div className="text-center text-muted-foreground">
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
            className="w-full h-full object-cover"
            onError={useMjpeg ? handleStreamError : handleImageError}
            onLoad={handleImageLoad}
          />
        )}
        
        {/* LIVE indicator matching Figma design */}
        <div className="absolute top-4 left-4 bg-red-600 text-white px-2 py-1 rounded text-xs font-medium flex items-center gap-1">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
          LIVE
        </div>
        
        {/* Fullscreen button matching Figma */}
        <button
          onClick={onFullscreen}
          className="absolute top-4 right-4 bg-black/60 hover:bg-black/80 text-white border-0 backdrop-blur-sm h-8 w-8 p-0 rounded"
        >
          ⛶
        </button>
        
        {/* Camera info overlay matching Figma */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-black/60 text-white px-3 py-2 rounded backdrop-blur-sm">
            <h3 className="text-sm font-medium">{title}</h3>
            <p className="text-xs text-white/80">{location}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
