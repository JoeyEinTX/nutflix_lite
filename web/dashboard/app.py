#!/usr/bin/env python3
"""
Nutflix Lite Web Dashboard
A minimal Flask + Flask-SocketIO web interface for monitoring and controlling the Nutflix system.
"""

import os
import threading
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import eventlet

# Use nutflix_common logger
from nutflix_common.logger import get_logger

# Get logger for web subsystem
logger = get_logger("web")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nutflix-development-key-change-in-production')

# Initialize SocketIO with eventlet
socketio = SocketIO(app, 
                   async_mode='eventlet',
                   cors_allowed_origins="*",
                   logger=False,
                   engineio_logger=False)

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
        
        <div class="status">
            <h2>Camera System</h2>
            <p><strong>CritterCam:</strong> <span id="critter-status">Initializing...</span></p>
            <p><strong>NutCam:</strong> <span id="nut-status">Initializing...</span></p>
        </div>
        
        <div class="status">
            <h2>Motion Detection</h2>
            <p><strong>Status:</strong> <span id="motion-status">Ready</span></p>
            <p><strong>Events Today:</strong> <span id="motion-events">0</span></p>
        </div>
    </div>

    <script>
        // Initialize SocketIO connection
        const socket = io();
        
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
        
        // Handle system status updates (for future expansion)
        socket.on('system_status', function(data) {
            console.log('System status:', data);
            // Update UI with system status
        });
        
        // Handle camera status updates (for future expansion)
        socket.on('camera_status', function(data) {
            console.log('Camera status:', data);
            // Update camera status in UI
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
    return {
        'status': 'healthy',
        'service': 'nutflix-dashboard',
        'version': '1.0.0'
    }

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
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected to dashboard")
    emit('system_status', {
        'status': 'connected',
        'message': 'Welcome to Nutflix Dashboard',
        'timestamp': eventlet.spawn(lambda: None).get_name()  # Simple timestamp
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
        # Use eventlet WSGI server for better performance with SocketIO
        socketio.run(app, 
                    host=host, 
                    port=port, 
                    debug=debug,
                    use_reloader=False,  # Disable reloader in production
                    log_output=False)    # Disable default Flask logging
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
