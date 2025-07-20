# NutFlix React Frontend Integration

This directory contains the React frontend for your NutFlix camera monitoring system.

## Quick Setup

1. **Install Node.js** (if not already installed):
   - Download from https://nodejs.org/
   - Choose the LTS version

2. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

3. **Development mode** (with Flask backend running on port 5050):
   ```bash
   npm run dev
   ```
   - React dev server will run on http://localhost:3000
   - API calls will proxy to your Flask backend on port 5050

4. **Production build** (serves from Flask):
   ```bash
   npm run build
   ```
   - Builds React app to `../web/static/`
   - Flask will serve the React app from http://localhost:5050

## Architecture

### Development Mode
- **React Dev Server**: http://localhost:3000 (frontend)
- **Flask Backend**: http://localhost:5050 (API + camera feeds)
- Vite proxy forwards API calls from React to Flask

### Production Mode
- **Flask Backend**: http://localhost:5050 (serves React + API + cameras)
- React app built into Flask's static directory

## Features

Your Figma design is now integrated with real camera functionality:

✅ **Real Camera Feeds**: Connected to your Raspberry Pi CSI cameras
✅ **Live WebSocket Updates**: Real-time status from Flask-SocketIO  
✅ **Professional UI**: Your Figma design with Tailwind CSS
✅ **Mobile Responsive**: Works on all devices
✅ **API Integration**: Flask serves data to React components

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── CameraFeed.tsx        # Live camera component
│   │   ├── SightingThumbnail.tsx # Wildlife activity cards
│   │   ├── FullscreenModal.tsx   # Modal for expanded views
│   │   ├── SquirrelBoxSensors.tsx # Environmental data
│   │   └── ui/                   # shadcn/ui components
│   ├── App.tsx                   # Main application
│   ├── globals.css               # Tailwind + custom styles
│   └── main.tsx                  # React entry point
├── package.json                  # Dependencies
├── vite.config.ts               # Build configuration
└── tailwind.config.js           # Styling configuration
```

## Flask Backend Enhancements

Your Flask app now has these new features:

- **React Frontend Serving**: `/` serves React app if built
- **Enhanced APIs**: 
  - `/api/status` - System status with timestamps
  - `/api/cameras` - Camera configuration and availability  
  - `/api/sightings` - Wildlife detection data (mock for now)
  - `/api/environmental` - Sensor data (mock for now)
- **SPA Support**: React Router works with Flask catch-all route

## Next Steps

1. **Start Development**:
   ```bash
   # Terminal 1: Start Flask backend
   python web_service.py
   
   # Terminal 2: Start React frontend  
   cd frontend && npm run dev
   ```

2. **Access Your App**:
   - **Development**: http://localhost:3000 (React with hot reload)
   - **Production**: http://localhost:5050 (Flask serving React)

3. **Customize**: 
   - Modify components in `src/components/`
   - Update styles in `src/globals.css`
   - Add real sensor data to Flask APIs

Your professional wildlife monitoring dashboard is ready! 🥜🐿️
