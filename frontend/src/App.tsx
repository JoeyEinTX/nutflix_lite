import React, { useState, useEffect } from 'react';
import { CameraFeed } from './components/CameraFeed';
import { SightingThumbnail } from './components/SightingThumbnail';
import { FullscreenModal } from './components/FullscreenModal';
import { SquirrelBoxSensors } from './components/SquirrelBoxSensors';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { io, Socket } from 'socket.io-client';
import './globals.css';

// Mock data for recent squirrel sightings (will be replaced with real data from Flask API)
const recentSightings = [
  {
    id: '1',
    animal: 'Eastern Gray Squirrel',
    location: 'CritterCam Feed',
    timestamp: new Date().toISOString(),
    image: 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&h=300&fit=crop'
  },
  {
    id: '2',
    animal: 'Red Squirrel',
    location: 'NutCam Feed',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    image: 'https://images.unsplash.com/photo-1512755816721-a9adabd2b6ae?w=400&h=300&fit=crop'
  },
  {
    id: '3',
    animal: 'Flying Squirrel',
    location: 'CritterCam Feed',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    image: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop'
  },
  {
    id: '4',
    animal: 'Fox Squirrel',
    location: 'NutCam Feed',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    image: 'https://images.unsplash.com/photo-1569454120577-b72b295d8c8a?w=400&h=300&fit=crop'
  }
];

// Map your Flask camera feeds to React component structure
const nutflixCameras = [
  {
    id: 'critter_cam',
    title: 'CritterCam',
    location: 'Raspberry Pi CSI-0 - Exterior Monitoring',
    streamUrl: '/video_feed/critter_cam',
    snapshotUrl: '/snapshot/critter_cam'
  },
  {
    id: 'nut_cam',
    title: 'NutCam',
    location: 'Raspberry Pi CSI-1 - Interior Monitoring',
    streamUrl: '/video_feed/nut_cam',
    snapshotUrl: '/snapshot/nut_cam'
  }
];

interface SystemStatus {
  cameras: {
    critter_cam: string;
    nut_cam: string;
  };
  motion_detection: string;
  system: string;
}

export default function App() {
  const [fullscreenModal, setFullscreenModal] = useState<{
    isOpen: boolean;
    type: 'camera' | 'sighting';
    title: string;
    content: any;
  }>({
    isOpen: false,
    type: 'camera',
    title: '',
    content: {}
  });

  const [carouselIndex, setCarouselIndex] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    cameras: {
      critter_cam: 'Initializing...',
      nut_cam: 'Initializing...'
    },
    motion_detection: 'ready',
    system: 'active'
  });
  const [socket, setSocket] = useState<Socket | null>(null);
  const [environmentalData, setEnvironmentalData] = useState({
    temperature: 42, // Default values, will be updated from sensors
    humidity: 65,
    lastUpdate: new Date().toISOString()
  });

  // Responsive items per view
  const itemsPerView = isMobile ? 1 : 3;
  const maxIndex = Math.max(0, recentSightings.length - itemsPerView);

  // Initialize WebSocket connection to Flask-SocketIO
  useEffect(() => {
    const newSocket = io('/', {
      transports: ['websocket', 'polling'],
      upgrade: true,
      rememberUpgrade: true,
      timeout: 5000,
      forceNew: true
    });

    newSocket.on('connect', () => {
      console.log('Connected to NutFlix Flask backend');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from NutFlix Flask backend');
    });

    newSocket.on('system_status', (data) => {
      console.log('System status update:', data);
      if (data.cameras) {
        setSystemStatus(prev => ({
          ...prev,
          cameras: data.cameras
        }));
      }
    });

    newSocket.on('camera_status', (data) => {
      console.log('Camera status update:', data);
      if (data.cameras) {
        setSystemStatus(prev => ({
          ...prev,
          cameras: data.cameras
        }));
      }
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  // Check if mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Reset carousel index when itemsPerView changes
  useEffect(() => {
    setCarouselIndex(0);
  }, [itemsPerView]);

  // Fetch system status from Flask API
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/status');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data);
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  // Calculate some quick stats
  const totalSightings = recentSightings.length;
  const uniqueSpecies = [...new Set(recentSightings.map(s => s.animal))].length;
  const todaysSightings = recentSightings.filter(s => 
    new Date(s.timestamp).toDateString() === new Date().toDateString()
  ).length;

  const openCameraFullscreen = (camera: typeof nutflixCameras[0]) => {
    setFullscreenModal({
      isOpen: true,
      type: 'camera',
      title: camera.title,
      content: { 
        location: camera.location,
        streamUrl: camera.streamUrl,
        snapshotUrl: camera.snapshotUrl
      }
    });
  };

  const openSightingFullscreen = (sighting: typeof recentSightings[0]) => {
    setFullscreenModal({
      isOpen: true,
      type: 'sighting',
      title: sighting.animal,
      content: sighting
    });
  };

  const closeModal = () => {
    setFullscreenModal({ ...fullscreenModal, isOpen: false });
  };

  const nextSlide = () => {
    setCarouselIndex(prev => Math.min(prev + 1, maxIndex));
  };

  const prevSlide = () => {
    setCarouselIndex(prev => Math.max(prev - 1, 0));
  };

  return (
    <div className="min-h-screen wildlife-gradient">
      {/* Header */}
      <header className="bg-stone-950/80 backdrop-blur-sm border-b border-stone-700 sticky top-0 z-40">
        <div className="container mx-auto px-6 py-6">
          <div className="flex justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-amber-200 mb-2">🥜 NutFlix</h1>
              <p className="text-stone-400 text-sm">Wildlife Monitoring System</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* System Status Indicator */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-stone-400">
            <div className={`w-2 h-2 rounded-full ${systemStatus.system === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            System Status: {systemStatus.system} | 
            CritterCam: {systemStatus.cameras.critter_cam} | 
            NutCam: {systemStatus.cameras.nut_cam}
          </div>
        </div>

        {/* My NutFlix System */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <h2 className="text-xl font-medium text-amber-200 flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              Live Camera Feeds
            </h2>
            {/* Environmental sensors */}
            <SquirrelBoxSensors
              temperature={environmentalData.temperature}
              humidity={environmentalData.humidity}
              lastUpdate={environmentalData.lastUpdate}
            />
          </div>
          
          {/* Responsive grid: 1 column on mobile, 2 columns on large screens */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {nutflixCameras.map((camera) => (
              <CameraFeed
                key={camera.id}
                id={camera.id}
                title={camera.title}
                location={camera.location}
                streamUrl={camera.streamUrl}
                snapshotUrl={camera.snapshotUrl}
                onFullscreen={() => openCameraFullscreen(camera)}
              />
            ))}
          </div>
        </section>

        {/* Recent Sightings Carousel */}
        <section>
          <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
            <h2 className="text-xl font-medium text-amber-200">Recent Wildlife Activity</h2>
            <div className="flex items-center gap-2">
              <Button
                onClick={prevSlide}
                disabled={carouselIndex === 0}
                size="sm"
                variant="outline"
                className="border-stone-600 hover:bg-stone-800 text-stone-300 disabled:opacity-50"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                onClick={nextSlide}
                disabled={carouselIndex >= maxIndex}
                size="sm"
                variant="outline"
                className="border-stone-600 hover:bg-stone-800 text-stone-300 disabled:opacity-50"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Activity stats */}
          <div className="flex items-center gap-3 mb-6 flex-wrap">
            <Badge variant="secondary" className="sensor-badge">
              {todaysSightings} today
            </Badge>
            <Badge variant="secondary" className="sensor-badge">
              {uniqueSpecies} species
            </Badge>
            <Badge variant="secondary" className="sensor-badge">
              {totalSightings} total sightings
            </Badge>
          </div>
          
          {/* Carousel container */}
          <div className="relative">
            <div className="overflow-hidden">
              <div 
                className="transition-transform duration-300 ease-in-out"
                style={{ 
                  transform: `translateX(-${carouselIndex * 100}%)`
                }}
              >
                <div className={`grid gap-4 ${isMobile ? 'grid-cols-1' : 'grid-cols-3'}`}>
                  {recentSightings.slice(carouselIndex * itemsPerView, (carouselIndex + 1) * itemsPerView).map((sighting) => (
                    <div key={sighting.id} className="w-full max-w-xs mx-auto">
                      <SightingThumbnail
                        {...sighting}
                        onClick={() => openSightingFullscreen(sighting)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Fullscreen Modal */}
      <FullscreenModal
        isOpen={fullscreenModal.isOpen}
        onClose={closeModal}
        title={fullscreenModal.title}
        type={fullscreenModal.type}
        content={fullscreenModal.content}
      />
    </div>
  );
}
