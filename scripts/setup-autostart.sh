#!/bin/bash
# Nutflix Auto-start Setup Script
# Run this script to enable auto-start on boot

echo "🚀 Setting up Nutflix auto-start services..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run this script as your regular user (not sudo)"
    echo "   The script will prompt for sudo when needed"
    exit 1
fi

# Get current user and home directory
CURRENT_USER=$(whoami)
CURRENT_HOME=$(eval echo ~$CURRENT_USER)
PROJECT_DIR="$CURRENT_HOME/nutflix/nutflix_lite"

echo "📁 User: $CURRENT_USER"
echo "📁 Home: $CURRENT_HOME"
echo "📁 Project: $PROJECT_DIR"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    echo "   Please update the paths in the service files"
    exit 1
fi

# Copy service files to systemd
echo "📋 Installing systemd service files..."
sudo cp "$PROJECT_DIR/scripts/nutflix.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/scripts/nutflix-web.service" /etc/systemd/system/

# Update service files with correct paths
echo "🔧 Updating service files with current user and paths..."
sudo sed -i "s|User=p12146|User=$CURRENT_USER|g" /etc/systemd/system/nutflix.service
sudo sed -i "s|Group=p12146|Group=$CURRENT_USER|g" /etc/systemd/system/nutflix.service
sudo sed -i "s|WorkingDirectory=/home/p12146/nutflix/nutflix_lite|WorkingDirectory=$PROJECT_DIR|g" /etc/systemd/system/nutflix.service
sudo sed -i "s|Environment=PATH=/home/p12146/nutflix/nutflix_lite/.venv/bin|Environment=PATH=$PROJECT_DIR/.venv/bin|g" /etc/systemd/system/nutflix.service
sudo sed -i "s|ExecStart=/home/p12146/nutflix/nutflix_lite/.venv/bin/python|ExecStart=$PROJECT_DIR/.venv/bin/python|g" /etc/systemd/system/nutflix.service
sudo sed -i "s|Environment=PYTHONPATH=/home/p12146/nutflix/nutflix_lite|Environment=PYTHONPATH=$PROJECT_DIR|g" /etc/systemd/system/nutflix.service

sudo sed -i "s|User=p12146|User=$CURRENT_USER|g" /etc/systemd/system/nutflix-web.service
sudo sed -i "s|Group=p12146|Group=$CURRENT_USER|g" /etc/systemd/system/nutflix-web.service
sudo sed -i "s|WorkingDirectory=/home/p12146/nutflix/nutflix_lite|WorkingDirectory=$PROJECT_DIR|g" /etc/systemd/system/nutflix-web.service
sudo sed -i "s|Environment=PATH=/home/p12146/nutflix/nutflix_lite/.venv/bin|Environment=PATH=$PROJECT_DIR/.venv/bin|g" /etc/systemd/system/nutflix-web.service
sudo sed -i "s|ExecStart=/home/p12146/nutflix/nutflix_lite/.venv/bin/python|ExecStart=$PROJECT_DIR/.venv/bin/python|g" /etc/systemd/system/nutflix-web.service
sudo sed -i "s|Environment=PYTHONPATH=/home/p12146/nutflix/nutflix_lite|Environment=PYTHONPATH=$PROJECT_DIR|g" /etc/systemd/system/nutflix-web.service

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable services
echo "✅ Enabling Nutflix services..."
sudo systemctl enable nutflix.service
sudo systemctl enable nutflix-web.service

echo ""
echo "🎉 Nutflix auto-start setup complete!"
echo ""
echo "📋 Available commands:"
echo "   sudo systemctl start nutflix         # Start camera system"
echo "   sudo systemctl start nutflix-web     # Start web dashboard"
echo "   sudo systemctl stop nutflix          # Stop camera system"
echo "   sudo systemctl stop nutflix-web      # Stop web dashboard"
echo "   sudo systemctl status nutflix        # Check camera system status"
echo "   sudo systemctl status nutflix-web    # Check web dashboard status"
echo "   sudo systemctl restart nutflix       # Restart camera system"
echo "   sudo systemctl restart nutflix-web   # Restart web dashboard"
echo ""
echo "📊 View logs:"
echo "   sudo journalctl -u nutflix -f        # Follow camera system logs"
echo "   sudo journalctl -u nutflix-web -f    # Follow web dashboard logs"
echo ""
echo "🚀 Services will now start automatically on boot!"
echo "🌐 Web dashboard will be available at: http://$(hostname -I | awk '{print $1}'):5000"
