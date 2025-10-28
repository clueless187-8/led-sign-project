#!/bin/bash
# Bandwidth Monitor Setup Script for Raspberry Pi Zero 2W
# Optimized for low-power 24/7 monitoring

set -e  # Exit on error

echo "========================================"
echo "Bandwidth Monitor - Pi Zero 2W Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo -e "${RED}Error: Not running on Raspberry Pi${NC}"
    exit 1
fi

PI_MODEL=$(cat /proc/device-tree/model)
echo "Detected: $PI_MODEL"
echo ""

# Check if it's a Pi Zero 2W
if [[ ! "$PI_MODEL" =~ "Pi Zero 2" ]]; then
    echo -e "${YELLOW}Warning: This script is optimized for Pi Zero 2W${NC}"
    echo "You're running on: $PI_MODEL"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Detect network connection type
echo "Checking network connection..."
HAS_ETHERNET=false
HAS_WIFI=false

if ip link show eth0 &> /dev/null && [ "$(cat /sys/class/net/eth0/operstate)" = "up" ]; then
    HAS_ETHERNET=true
    ETH_SPEED=$(ethtool eth0 2>/dev/null | grep "Speed:" | awk '{print $2}' || echo "unknown")
    echo -e "${GREEN}✓ Ethernet detected: $ETH_SPEED${NC}"
elif ip link show eth0 &> /dev/null; then
    echo -e "${YELLOW}⚠ Ethernet adapter detected but not connected${NC}"
else
    echo -e "${YELLOW}⚠ No Ethernet adapter found${NC}"
fi

if ip link show wlan0 &> /dev/null && [ "$(cat /sys/class/net/wlan0/operstate)" = "up" ]; then
    HAS_WIFI=true
    WIFI_SSID=$(iwgetid -r 2>/dev/null || echo "unknown")
    WIFI_QUALITY=$(iwconfig wlan0 2>/dev/null | grep "Link Quality" | awk -F'[=/]' '{print int($2/$3*100)}' || echo "unknown")
    echo -e "${GREEN}✓ WiFi connected: $WIFI_SSID (Quality: ${WIFI_QUALITY}%)${NC}"
fi

if [ "$HAS_ETHERNET" = false ] && [ "$HAS_WIFI" = false ]; then
    echo -e "${RED}Error: No network connection detected${NC}"
    exit 1
fi

echo ""

# Network performance warning
if [ "$HAS_ETHERNET" = false ] && [ "$HAS_WIFI" = true ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠  IMPORTANT: WiFi Speed Limitation${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Pi Zero 2W WiFi typically maxes out at 20-40 Mbps"
    echo "To test full Xfinity speeds (800+ Mbps), you need:"
    echo "  • USB Ethernet adapter (Gigabit preferred)"
    echo "  • USB OTG cable/adapter"
    echo ""
    echo "WiFi monitoring is still useful for:"
    echo "  • Detecting throttling patterns over time"
    echo "  • Monitoring WiFi performance"
    echo "  • Relative speed comparisons"
    echo ""
    read -p "Continue with WiFi-only setup? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please connect Ethernet adapter and re-run this script"
        exit 1
    fi
fi

echo ""
echo "Updating system packages..."
sudo apt update

echo ""
echo "Installing required packages..."
sudo apt install -y python3-pip python3-dev sqlite3 git

echo ""
echo "Installing Python dependencies..."
cd ~/led-sign-project 2>/dev/null || cd /home/pi/led-sign-project || {
    echo -e "${RED}Error: led-sign-project directory not found${NC}"
    echo "Please ensure the project is in ~/led-sign-project"
    exit 1
}

pip3 install -r requirements.txt

# Test speedtest-cli
echo ""
echo "Testing speedtest-cli installation..."
if python3 -c "import speedtest" 2>/dev/null; then
    echo -e "${GREEN}✓ speedtest-cli installed successfully${NC}"
else
    echo -e "${RED}Error: speedtest-cli installation failed${NC}"
    exit 1
fi

# Make scripts executable
chmod +x bandwidth_monitor.py
chmod +x bandwidth_dashboard.py

echo ""
echo "Running initial speed test..."
echo "(This may take 30-60 seconds)"
python3 bandwidth_monitor.py --once

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Speed test completed successfully${NC}"
else
    echo -e "${YELLOW}⚠ Speed test had issues, but continuing...${NC}"
fi

# Create systemd service for bandwidth monitor
echo ""
echo "Setting up systemd service for bandwidth monitoring..."

sudo tee /etc/systemd/system/bandwidth-monitor.service > /dev/null <<EOF
[Unit]
Description=Bandwidth Monitor Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
ExecStart=/usr/bin/python3 $PWD/bandwidth_monitor.py --interval 300 --threshold 800
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Created bandwidth-monitor.service${NC}"

# Create systemd service for dashboard
echo ""
echo "Setting up systemd service for web dashboard..."

sudo tee /etc/systemd/system/bandwidth-dashboard.service > /dev/null <<EOF
[Unit]
Description=Bandwidth Dashboard Web Interface
After=network-online.target bandwidth-monitor.service
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
ExecStart=/usr/bin/python3 $PWD/bandwidth_dashboard.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Created bandwidth-dashboard.service${NC}"

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "1. Enable and start monitoring service:"
echo "   ${GREEN}sudo systemctl enable bandwidth-monitor.service${NC}"
echo "   ${GREEN}sudo systemctl start bandwidth-monitor.service${NC}"
echo ""
echo "2. Enable and start dashboard service:"
echo "   ${GREEN}sudo systemctl enable bandwidth-dashboard.service${NC}"
echo "   ${GREEN}sudo systemctl start bandwidth-dashboard.service${NC}"
echo ""
echo "3. Check service status:"
echo "   ${GREEN}sudo systemctl status bandwidth-monitor.service${NC}"
echo "   ${GREEN}sudo systemctl status bandwidth-dashboard.service${NC}"
echo ""
echo "4. View logs:"
echo "   ${GREEN}journalctl -u bandwidth-monitor.service -f${NC}"
echo "   ${GREEN}journalctl -u bandwidth-dashboard.service -f${NC}"
echo ""
echo "5. Access web dashboard:"
echo "   From any device on your network:"
echo "   ${GREEN}http://$(hostname -I | awk '{print $1}'):5001${NC}"
echo "   ${GREEN}http://$(hostname).local:5001${NC}"
echo ""
echo "Configuration:"
echo "  • Test interval: 5 minutes (300 seconds)"
echo "  • Alert threshold: 800 Mbps"
echo "  • Database: $PWD/bandwidth_data.db"
echo "  • Logs: $PWD/bandwidth_monitor.log"
echo ""

# Auto-start prompt
echo ""
read -p "Start monitoring services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Enabling and starting services..."
    sudo systemctl enable bandwidth-monitor.service
    sudo systemctl start bandwidth-monitor.service
    sudo systemctl enable bandwidth-dashboard.service
    sudo systemctl start bandwidth-dashboard.service

    sleep 2

    echo ""
    echo "Service status:"
    sudo systemctl status bandwidth-monitor.service --no-pager -l
    echo ""
    sudo systemctl status bandwidth-dashboard.service --no-pager -l

    echo ""
    echo -e "${GREEN}✓ Services are running!${NC}"
    echo ""
    echo "Dashboard available at:"
    echo -e "${GREEN}http://$(hostname -I | awk '{print $1}'):5001${NC}"
else
    echo ""
    echo "Services not started. Start them manually when ready:"
    echo "  sudo systemctl start bandwidth-monitor.service"
    echo "  sudo systemctl start bandwidth-dashboard.service"
fi

echo ""
echo "Setup complete! See PI_ZERO_2W_GUIDE.md for detailed configuration."
echo ""
