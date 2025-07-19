import { useState, useEffect } from 'react';
import { CameraFeed } from './components/CameraFeed';
import { FullscreenModal } from './components/FullscreenModal';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
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

  const [isMobile, setIsMobile] = useState(false);
  const [environmentalData] = useState({
    temperature: 42, // Default values, will be updated from sensors
    humidity: 65,
    lastUpdate: new Date().toISOString()
  });

  // Check if mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
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

  const closeModal = () => {
    setFullscreenModal({ ...fullscreenModal, isOpen: false });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header with proper Figma spacing and typography */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center justify-center">
            <div className="flex items-center gap-3">
              {/* NutFlix logo with acorn icon matching Figma */}
              <div className="text-4xl">🥜</div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                NUTFLIX
              </h1>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 space-y-8">
        {/* System header section matching Figma layout */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h2 className="text-2xl font-semibold text-foreground flex items-center gap-3">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                My SquirrelBox
              </h2>
            </div>
            
            {/* System status with proper Figma styling */}
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-foreground">{environmentalData.temperature}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-foreground">{environmentalData.humidity}</span>
              </div>
              <div className="text-xs">
                Updated {environmentalData.lastUpdate}
              </div>
            </div>
          </div>
        </section>

        {/* Live Camera Feeds Section - Figma Design */}
        <section className="space-y-6">
          {/* Camera feeds grid with proper Figma spacing */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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

        {/* Recent Wildlife Activity */}
        <section className="space-y-6">
          <h2 className="text-xl font-semibold text-foreground">Recent Wildlife Activity</h2>
          
          {/* Activity stats */}
          <div className="flex items-center gap-3 flex-wrap">
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
              {todaysSightings} today
            </Badge>
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
              {uniqueSpecies} species
            </Badge>
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
              {totalSightings} total sightings
            </Badge>
          </div>
          
          {/* Activity feed */}
          <div className="space-y-4">
            {[
              { 
                time: '2m ago', 
                animal: 'Red Squirrel', 
                location: 'Feeder Station A', 
                activity: 'Feeding detected',
                confidence: 95,
                icon: '🐿️'
              },
              { 
                time: '8m ago', 
                animal: 'Blue Jay', 
                location: 'Water Feature', 
                activity: 'Drinking observed',
                confidence: 88,
                icon: '🐦'
              },
              { 
                time: '15m ago', 
                animal: 'Rabbit', 
                location: 'Garden Area', 
                activity: 'Foraging behavior',
                confidence: 92,
                icon: '🐰'
              },
            ].map((activity, index) => (
              <div 
                key={index} 
                className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="text-2xl">{activity.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-medium text-foreground">{activity.animal}</h3>
                        <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                          {activity.confidence}% confident
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-1">{activity.location}</p>
                      <p className="text-sm text-foreground">{activity.activity}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-muted-foreground">{activity.time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* View All Button */}
          <div className="text-center">
            <Button variant="outline" className="bg-background hover:bg-muted border-border">
              View All Activity
            </Button>
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
