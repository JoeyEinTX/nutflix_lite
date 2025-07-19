#!/usr/bin/env python3
"""
Nutflix Lite Web Dashboard
A minimal Flask + Flask-SocketIO web interface for monitoring and controlling the Nutflix system.
"""

import os
import threading
import sys
import time
from flask import Flask, render_template_string, request, jsonify, Response
from flask_socketio import SocketIO, emit
import eventlet

# Add the parent directory to the path to import camera_manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Use nutflix_common logger
from nutflix_common.logger import get_logger

# Get logger for web subsystem
logger = get_logger("web")

# Global camera manager instance (will be set by main app)
camera_manager = None

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nutflix-development-key-change-in-production')

# Initialize SocketIO with threading mode for better MJPEG compatibility
socketio = SocketIO(app, 
                   async_mode='threading',
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=False)

# Global system status
system_status = {
    'cameras': {
        'critter_cam': 'Initializing...',
        'nut_cam': 'Initializing...'
    },
    'motion_detection': 'ready',
    'system': 'active'
}

# Simple HTML template for the main page
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nutflix Lite Dashboard</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #111;
            color: #0f0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            background-color: #222;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .connection-status {
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            text-align: center;
        }
        .connected {
            background-color: #2d5016;
            color: #4caf50;
        }
        .disconnected {
            background-color: #5d1e1e;
            color: #f44336;
        }
        .camera-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .camera-feed {
            background-color: #222;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .camera-feed h3 {
            margin-top: 0;
            color: #0f0;
        }
        .camera-image {
            width: 100%;
            max-width: 400px;
            height: auto;
            border: 2px solid #444;
            border-radius: 4px;
            background-color: #111;
        }
        .camera-status {
            margin-top: 10px;
            font-weight: bold;
        }
        .status-ready {
            color: #4caf50;
        }
        .status-initializing {
            color: #ff9800;
        }
        .status-error {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🥜 Welcome to Nutflix Lite Dashboard</h1>
            <p>Real-time monitoring and control for your dual-camera system</p>
        </div>
        
        <div class="status">
            <h2>System Status</h2>
            <p><strong>Dashboard:</strong> Active</p>
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Mode:</strong> Production Ready</p>
            
            <div id="connection-status" class="connection-status disconnected">
                🔴 WebSocket: Disconnected
            </div>
        </div>
        
        <div class="camera-grid">
            <div class="camera-feed">
                <h3>🐿️ Critter Cam</h3>
                <img id="critter-feed" class="camera-image" src="/video_feed/critter_cam" alt="Critter Camera Feed">
                <div class="camera-status">
                    Status: <span id="critter-status" class="status-initializing">Initializing...</span>
                </div>
            </div>
            
            <div class="camera-feed">
                <h3>🥜 Nut Cam</h3>
                <img id="nut-feed" class="camera-image" src="/video_feed/nut_cam" alt="Nut Camera Feed">
                <div class="camera-status">
                    Status: <span id="nut-status" class="status-initializing">Initializing...</span>
                </div>
            </div>
        </div>
        
        <div class="status">
            <h2>Camera System</h2>
            <p><strong>CritterCam:</strong> <span id="critter-status-text">Initializing...</span></p>
            <p><strong>NutCam:</strong> <span id="nut-status-text">Initializing...</span></p>
        </div>
        
        <div class="status">
            <h2>Motion Detection</h2>
            <p><strong>Status:</strong> <span id="motion-status">Ready</span></p>
            <p><strong>Events Today:</strong> <span id="motion-events">0</span></p>
        </div>
    </div>

    <script>
        // Initialize SocketIO connection with explicit v4 options
        const socket = io({
            transports: ['websocket', 'polling'],
            upgrade: true,
            rememberUpgrade: true,
            timeout: 5000,
            forceNew: true
        });
        
        // Connection status elements
        const connectionStatus = document.getElementById('connection-status');
        
        // Handle connection events
        socket.on('connect', function() {
            console.log('Connected to Nutflix server');
            connectionStatus.textContent = '🟢 WebSocket: Connected';
            connectionStatus.className = 'connection-status connected';
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from Nutflix server');
            connectionStatus.textContent = '🔴 WebSocket: Disconnected';
            connectionStatus.className = 'connection-status disconnected';
        });
        
        socket.on('connect_error', function(error) {
            console.error('Connection error:', error);
            connectionStatus.textContent = '🔴 WebSocket: Connection Error';
            connectionStatus.className = 'connection-status disconnected';
        });
        
        // Handle system status updates (for future expansion)
        socket.on('system_status', function(data) {
            console.log('System status:', data);
            // Update UI with system status
        });
        
        // Handle camera status updates (for future expansion)
        socket.on('camera_status', function(data) {
            console.log('Camera status:', data);
            
            // Update camera status displays
            if (data.cameras) {
                // Update critter cam status
                if (data.cameras.critter_cam) {
                    updateCameraStatus('critter', data.cameras.critter_cam);
                }
                
                // Update nut cam status  
                if (data.cameras.nut_cam) {
                    updateCameraStatus('nut', data.cameras.nut_cam);
                }
            }
        });
        
        function updateCameraStatus(camera, status) {
            // Update status text elements
            const statusElement = document.getElementById(camera + '-status');
            const statusTextElement = document.getElementById(camera + '-status-text');
            
            if (statusElement) {
                statusElement.textContent = status;
                // Update CSS class based on status
                statusElement.className = getStatusClass(status);
            }
            
            if (statusTextElement) {
                statusTextElement.textContent = status;
            }
        }
        
        function getStatusClass(status) {
            const lowerStatus = status.toLowerCase();
            if (lowerStatus.includes('ready') || lowerStatus.includes('active')) {
                return 'status-ready';
            } else if (lowerStatus.includes('initializing') || lowerStatus.includes('starting')) {
                return 'status-initializing';
            } else {
                return 'status-error';
            }
        }
        
        // Handle image load errors (fallback for camera feeds)
        document.addEventListener('DOMContentLoaded', function() {
            const critterFeed = document.getElementById('critter-feed');
            const nutFeed = document.getElementById('nut-feed');
            
            critterFeed.onerror = function() {
                console.log('Critter cam feed error, retrying...');
                setTimeout(() => {
                    this.src = '/video_feed/critter_cam?' + new Date().getTime();
                }, 2000);
            };
            
            nutFeed.onerror = function() {
                console.log('Nut cam feed error, retrying...');
                setTimeout(() => {
                    this.src = '/video_feed/nut_cam?' + new Date().getTime();
                }, 2000);
            };
        });
        
        // Handle motion detection events (for future expansion)
        socket.on('motion_detected', function(data) {
            console.log('Motion detected:', data);
            // Update motion detection UI
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard page."""
    logger.info("Dashboard accessed")
    return render_template_string(MAIN_PAGE_HTML)

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    camera_status = 'not_available'
    camera_details = {}
    
    if camera_manager is not None:
        try:
            camera_status = 'available'
            camera_details = {
                'critter_cam_available': camera_manager.is_camera_available('critter_cam'),
                'nut_cam_available': camera_manager.is_camera_available('nut_cam'),
                'camera_info': camera_manager.get_camera_info()
            }
        except Exception as e:
            camera_status = f'error: {str(e)}'
            logger.error(f"Error checking camera status: {e}")
    
    return {
        'status': 'healthy',
        'service': 'nutflix-dashboard',
        'version': '1.0.0',
        'camera_manager': camera_status,
        'camera_details': camera_details
    }

@app.route('/debug/camera_manager_status')
def debug_camera_manager_status():
    """Debug endpoint to check camera manager status."""
    global camera_manager
    
    status = {
        'camera_manager_global': camera_manager is not None,
        'camera_manager_type': str(type(camera_manager)) if camera_manager else 'None',
    }
    
    if camera_manager:
        try:
            status['camera_info'] = camera_manager.get_camera_info()
            status['critter_available'] = camera_manager.is_camera_available('critter_cam')
            status['nut_available'] = camera_manager.is_camera_available('nut_cam')
        except Exception as e:
            status['error'] = str(e)
    
    return jsonify(status)

@app.route('/debug/camera_test/<camera_name>')
def debug_camera_test(camera_name):
    """Debug endpoint to test camera manager."""
    if camera_manager is None:
        return jsonify({'error': 'Camera manager not available'}), 503
    
    try:
        frame_bytes = camera_manager.get_latest_frame(camera_name)
        if frame_bytes:
            return Response(frame_bytes, mimetype='image/jpeg')
        else:
            return jsonify({'error': f'No frame available from {camera_name}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint for system status (for future integration)."""
    return {
        'dashboard': 'active',
        'cameras': {
            'critter_cam': 'unknown',
            'nut_cam': 'unknown'
        },
        'motion_detection': 'ready'
    }

# SocketIO event handlers
@socketio.on('connect')
def handle_connect(auth):
    """Handle client connection."""
    logger.info("Client connected to dashboard")
    emit('system_status', {
        'status': 'connected',
        'message': 'Welcome to Nutflix Dashboard',
        'timestamp': str(time.time())  # Simple timestamp
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected from dashboard")

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client."""
    logger.debug("Status requested by client")
    emit('system_status', {
        'dashboard': 'active',
        'cameras': 'initialized',
        'motion_detection': 'ready'
    })

# REST API endpoints
@app.route('/api/status', methods=['POST'])
def update_status():
    """Receive status updates from the main camera system."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        logger.debug(f"Received status update: {data}")
        
        # Update global status
        global system_status
        if 'cameras' in data:
            system_status['cameras'].update(data['cameras'])
        if 'motion_detection' in data:
            system_status['motion_detection'] = data['motion_detection']
        if 'system' in data:
            system_status['system'] = data['system']
        
        # Emit status update to all connected clients
        socketio.emit('camera_status', system_status)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status."""
    return jsonify(system_status)

@app.route('/video_feed/<camera_name>')
def video_feed(camera_name):
    """
    Video streaming route. Returns an MJPEG stream for the specified camera.
    
    Args:
        camera_name: Either 'critter_cam' or 'nut_cam'
    """
    logger.info(f"Video feed requested for {camera_name}")
    
    if camera_name not in ['critter_cam', 'nut_cam']:
        logger.warning(f"Invalid camera name requested: {camera_name}")
        return "Invalid camera name", 404
    
    # Check if camera manager is available
    if camera_manager is None:
        logger.error(f"Camera manager not available for {camera_name}")
        return "Camera manager not available", 503
    
    # Check if specific camera is available
    if not camera_manager.is_camera_available(camera_name):
        logger.warning(f"Camera {camera_name} is not available")
        return f"Camera {camera_name} not available", 503
    
    def generate_frames():
        """Generate frames for MJPEG streaming."""
        frame_count = 0
        consecutive_failures = 0
        max_failures = 50  # Stop after 50 consecutive failures
        
        while consecutive_failures < max_failures:
            try:
                frame_count += 1
                
                # Get frame from camera manager
                frame_bytes = camera_manager.get_latest_frame(camera_name)
                
                if frame_bytes is not None:
                    consecutive_failures = 0  # Reset failure counter
                    
                    # Log success occasionally
                    if frame_count % 100 == 0:
                        logger.debug(f"Serving frame {frame_count} for {camera_name}, size: {len(frame_bytes)} bytes")
                    
                    # Return the frame in MJPEG format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    consecutive_failures += 1
                    
                    # Log when no frame available
                    if consecutive_failures % 10 == 0:
                        logger.warning(f"No frame available from {camera_name} (failure {consecutive_failures})")
                    
                    # Return placeholder if no frame available
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + 
                           create_placeholder_frame(camera_name) + b'\r\n')
                
                # Limit to ~10 FPS
                time.sleep(0.1)
                
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error in video feed for {camera_name} (failure {consecutive_failures}): {e}")
                
                # Return error placeholder
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + 
                       create_placeholder_frame(f"{camera_name} ERROR") + b'\r\n')
                time.sleep(1)  # Wait longer on error
        
        logger.error(f"Video feed for {camera_name} stopped after {max_failures} consecutive failures")
    
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def create_placeholder_frame(camera_name):
    """Create a simple placeholder image when camera is not available."""
    try:
        import cv2
        import numpy as np
        
        # Create a simple 640x480 placeholder image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img.fill(32)  # Dark gray background
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = f"{camera_name.replace('_', ' ').title()}"
        status_text = "Initializing..."
        
        # Calculate text size and position
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        status_size = cv2.getTextSize(status_text, font, 0.7, 2)[0]
        
        # Center the text
        text_x = (640 - text_size[0]) // 2
        text_y = (480 - text_size[1]) // 2 - 20
        status_x = (640 - status_size[0]) // 2
        status_y = text_y + 40
        
        # Draw text
        cv2.putText(img, text, (text_x, text_y), font, 1, (0, 255, 0), 2)
        cv2.putText(img, status_text, (status_x, status_y), font, 0.7, (0, 255, 255), 2)
        
        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return buffer.tobytes()
        
    except Exception as e:
        logger.error(f"Error creating placeholder frame: {e}")
        # Return minimal valid JPEG header for 1x1 black pixel
        return (b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
                b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n'
                b'\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d'
                b'\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
                b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01'
                b'\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01'
                b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07'
                b'\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03'
                b'\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A'
                b'\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br'
                b'\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghij'
                b'klmnopqrstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95'
                b'\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3'
                b'\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca'
                b'\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7'
                b'\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00'
                b'\x08\x01\x01\x00\x00?\x00\xf7\xfa(\xa2\x80\x0f\xff\xd9')

def set_camera_manager(cm):
    """Set the camera manager instance for video feeds."""
    global camera_manager
    logger.info(f"set_camera_manager called with: {type(cm) if cm else 'None'}")
    camera_manager = cm
    if cm:
        logger.info("Camera manager successfully set for web dashboard")
    else:
        logger.warning("Camera manager set to None!")
    
    # Immediate test
    try:
        if camera_manager:
            logger.info(f"Testing camera manager: {camera_manager.get_camera_info()}")
        else:
            logger.error("Camera manager is None after setting!")
    except Exception as e:
        logger.error(f"Error testing camera manager: {e}")

def run_web_server(app_context=None, host='0.0.0.0', port=5000, debug=False):
    """
    Run the Flask-SocketIO web server.
    
    Args:
        app_context: Optional application context (for future integration)
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 5000)
        debug: Enable debug mode (default: False)
    """
    logger.info(f"Starting Nutflix web dashboard on {host}:{port}")
    
    if app_context:
        logger.info("Web server initialized with application context")
        # Store app context for future use
        app.config['NUTFLIX_CONTEXT'] = app_context
    
    try:
        # Use threading WSGI server for better performance with SocketIO and MJPEG
        socketio.run(app, 
                    host=host, 
                    port=port, 
                    debug=debug,
                    use_reloader=False,  # Disable reloader in production
                    log_output=False,    # Disable default Flask logging
                    allow_unsafe_werkzeug=True)  # Allow Werkzeug for local production
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        raise

def run_web_server_threaded(app_context=None, host='0.0.0.0', port=5000, debug=False):
    """
    Run the web server in a separate thread (for integration with main app).
    
    Args:
        app_context: Optional application context
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
        
    Returns:
        threading.Thread: The thread running the web server
    """
    def server_thread():
        run_web_server(app_context, host, port, debug)
    
    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()
    logger.info(f"Web server started in background thread on {host}:{port}")
    return thread

# For testing and development
if __name__ == "__main__":
    logger.info("Starting Nutflix Dashboard in standalone mode")
    run_web_server(debug=True)
