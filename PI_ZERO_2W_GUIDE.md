# Bandwidth Monitor - Raspberry Pi Zero 2W Complete Guide

Complete setup and configuration guide for running the bandwidth monitor on a Raspberry Pi Zero 2W.

## Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Initial Pi Setup](#initial-pi-setup)
3. [Network Configuration](#network-configuration)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Monitoring & Management](#monitoring--management)
7. [Troubleshooting](#troubleshooting)
8. [Optimization Tips](#optimization-tips)

---

## Hardware Requirements

### Essential
- **Raspberry Pi Zero 2W** (~$15)
- **MicroSD Card** (8GB minimum, 16GB+ recommended, Class 10)
- **USB Power Supply** (5V 2.5A recommended)
- **MicroSD Card Reader** (for initial setup)

### Highly Recommended for Accurate Results
- **USB OTG Cable/Adapter** (~$5)
- **USB Ethernet Adapter** (~$10-15)
  - Recommended: USB 2.0 to Gigabit Ethernet (RTL8153 chipset)
  - Supports 100/1000 Mbps
  - Example: UGREEN, Cable Matters, TP-Link UE300

### Optional
- **Case** (protects the Pi)
- **Heatsink** (helps with thermal management)

### Why Ethernet Adapter?

| Connection | Max Speed | Best For |
|------------|-----------|----------|
| Built-in WiFi | ~20-40 Mbps | WiFi performance monitoring, patterns |
| USB Ethernet | 1000 Mbps | Testing full Xfinity speed (800+ Mbps) |

**Verdict:** For monitoring Xfinity 800 Mbps threshold, use Ethernet adapter.

---

## Initial Pi Setup

### 1. Flash Raspberry Pi OS

**Using Raspberry Pi Imager (Recommended):**

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert microSD card
3. Choose OS: **Raspberry Pi OS Lite (64-bit)** - headless, no desktop
4. Click gear icon ⚙️ for advanced options:
   - Set hostname: `bandwidth-monitor`
   - Enable SSH
   - Set username/password (default: pi/raspberry)
   - Configure WiFi (SSID and password)
   - Set timezone
5. Write to SD card

### 2. Boot and Connect

```bash
# Insert SD card into Pi Zero 2W and power on
# Wait 60 seconds for first boot

# SSH into the Pi
ssh pi@bandwidth-monitor.local
# OR
ssh pi@[PI_IP_ADDRESS]

# Default password: raspberry (or what you set in imager)
```

### 3. Initial Configuration

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install useful tools
sudo apt install -y vim htop git curl net-tools ethtool wireless-tools

# Optional: Configure using raspi-config
sudo raspi-config
```

In `raspi-config`:
- System Options → Hostname (e.g., "bandwidth-monitor")
- Interface Options → Enable SSH (if not already)
- Localisation Options → Set timezone
- Performance Options → GPU Memory → Set to 16MB (we don't need GPU)
- Finish and reboot

---

## Network Configuration

### Option A: Ethernet Adapter (Recommended)

1. **Connect Hardware:**
   - USB OTG adapter → Pi Zero 2W
   - USB Ethernet adapter → OTG adapter
   - Ethernet cable → Router

2. **Verify Connection:**
   ```bash
   # Check interface
   ip link show eth0

   # Should show state UP
   ip addr show eth0

   # Check speed
   sudo ethtool eth0 | grep Speed
   # Should show: Speed: 1000Mb/s (for Gigabit)
   ```

3. **Test Speed:**
   ```bash
   # Quick test
   curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -
   ```

### Option B: WiFi Only

1. **Check WiFi Status:**
   ```bash
   iwconfig wlan0
   ip addr show wlan0
   ```

2. **Optimize WiFi:**
   ```bash
   # Disable WiFi power management (improves consistency)
   sudo iw dev wlan0 set power_save off

   # Make permanent
   sudo tee /etc/rc.local > /dev/null <<EOF
   #!/bin/sh -e
   iw dev wlan0 set power_save off
   exit 0
   EOF
   sudo chmod +x /etc/rc.local
   ```

3. **Position Pi:**
   - Place close to router (line of sight if possible)
   - Avoid metal enclosures
   - Test signal: `iwconfig wlan0 | grep Quality`

### Static IP (Optional but Recommended)

Makes dashboard access easier:

```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add to bottom (adjust for your network):
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# OR for WiFi:
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Save (Ctrl+O, Enter, Ctrl+X)
sudo reboot
```

---

## Installation

### Method 1: Automated Setup Script (Easiest)

```bash
# Clone or download the project
cd ~
git clone https://github.com/YOUR_USERNAME/led-sign-project.git
# OR download and extract files

cd led-sign-project

# Run setup script
chmod +x setup_pi_zero_2w.sh
./setup_pi_zero_2w.sh
```

The script will:
- Detect your Pi model
- Check network configuration
- Install all dependencies
- Run initial speed test
- Create systemd services
- Offer to start services automatically

### Method 2: Manual Installation

```bash
cd ~/led-sign-project

# Install Python dependencies
pip3 install -r requirements.txt

# Make scripts executable
chmod +x bandwidth_monitor.py
chmod +x bandwidth_dashboard.py

# Test installation
python3 bandwidth_monitor.py --once

# Check results
cat bandwidth_monitor.log
```

---

## Configuration

### Adjust Monitoring Settings

Edit monitoring parameters:

```bash
# Test every 3 minutes instead of 5
python3 bandwidth_monitor.py --interval 180 --threshold 800

# Lower threshold to 700 Mbps
python3 bandwidth_monitor.py --interval 300 --threshold 700
```

### Systemd Service Configuration

Edit service to change defaults:

```bash
sudo nano /etc/systemd/system/bandwidth-monitor.service
```

Modify the `ExecStart` line:

```ini
# Example: Test every 10 minutes with 900 Mbps threshold
ExecStart=/usr/bin/python3 /home/pi/led-sign-project/bandwidth_monitor.py --interval 600 --threshold 900
```

Reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart bandwidth-monitor.service
```

### Dashboard Port Configuration

Change dashboard port (default 5001):

```bash
nano ~/led-sign-project/bandwidth_dashboard.py
```

Find the last line and change port:

```python
app.run(host='0.0.0.0', port=8080, debug=False)  # Changed to 8080
```

---

## Monitoring & Management

### Service Control

```bash
# Start services
sudo systemctl start bandwidth-monitor.service
sudo systemctl start bandwidth-dashboard.service

# Stop services
sudo systemctl stop bandwidth-monitor.service
sudo systemctl stop bandwidth-dashboard.service

# Restart services
sudo systemctl restart bandwidth-monitor.service
sudo systemctl restart bandwidth-dashboard.service

# Check status
sudo systemctl status bandwidth-monitor.service
sudo systemctl status bandwidth-dashboard.service

# Enable auto-start on boot
sudo systemctl enable bandwidth-monitor.service
sudo systemctl enable bandwidth-dashboard.service

# Disable auto-start
sudo systemctl disable bandwidth-monitor.service
sudo systemctl disable bandwidth-dashboard.service
```

### View Logs

```bash
# Real-time monitoring logs
journalctl -u bandwidth-monitor.service -f

# Real-time dashboard logs
journalctl -u bandwidth-dashboard.service -f

# Last 100 lines
journalctl -u bandwidth-monitor.service -n 100

# Today's logs only
journalctl -u bandwidth-monitor.service --since today

# Check application log files
tail -f ~/led-sign-project/bandwidth_monitor.log
cat ~/led-sign-project/bandwidth_alerts.txt
```

### Database Management

```bash
# View database location
ls -lh ~/led-sign-project/bandwidth_data.db

# Connect to database
sqlite3 ~/led-sign-project/bandwidth_data.db

# Useful queries:
sqlite> .tables
sqlite> SELECT COUNT(*) FROM speed_tests;
sqlite> SELECT timestamp, download_mbps FROM speed_tests ORDER BY timestamp DESC LIMIT 10;
sqlite> SELECT AVG(download_mbps) FROM speed_tests WHERE timestamp >= datetime('now', '-24 hours');
sqlite> .quit
```

### Backup Data

```bash
# Backup database
cp ~/led-sign-project/bandwidth_data.db ~/bandwidth_data_backup_$(date +%Y%m%d).db

# Backup to another machine
scp pi@bandwidth-monitor.local:~/led-sign-project/bandwidth_data.db ./
```

### Access Dashboard

From any device on your network:

```bash
# Using hostname
http://bandwidth-monitor.local:5001

# Using IP address
http://192.168.1.100:5001  # Replace with your Pi's IP
```

From your phone:
- Connect to same WiFi
- Open browser
- Enter: `http://bandwidth-monitor.local:5001`

---

## Troubleshooting

### Pi Won't Boot

1. Check power supply (needs 5V 2.5A)
2. Try different microSD card
3. Re-flash OS
4. Check LED indicators:
   - Solid red: Power OK
   - Flashing green: SD card activity (should flash on boot)

### Can't SSH to Pi

```bash
# Try IP directly (check router for assigned IP)
ssh pi@192.168.1.XXX

# If using WiFi, ensure correct credentials in imager

# Check if SSH is enabled
# Re-flash with SSH enabled in Imager settings
```

### Speed Tests Failing

```bash
# Test speedtest-cli manually
python3 -c "import speedtest; st = speedtest.Speedtest(); print(st.download() / 1000000)"

# Try different speedtest server
speedtest-cli --list | grep -i "your city"
speedtest-cli --server SERVER_ID

# Check network connectivity
ping -c 4 8.8.8.8

# Check DNS
nslookup google.com
```

### Ethernet Not Detected

```bash
# Check if adapter is recognized
lsusb
# Look for network adapter

# Check interface
ip link show

# If no eth0, may need drivers
sudo apt update
sudo apt install -y linux-modules-extra-raspi

# Check kernel messages
dmesg | grep -i eth
dmesg | grep -i usb
```

### Dashboard Not Accessible

```bash
# Check if service is running
sudo systemctl status bandwidth-dashboard.service

# Check if port is listening
sudo netstat -tulpn | grep :5001

# Test locally on Pi
curl http://localhost:5001

# Check firewall (usually not enabled by default)
sudo ufw status

# If firewall enabled, allow port
sudo ufw allow 5001
```

### High CPU Usage

```bash
# Check CPU usage
htop

# If speedtest-cli is using too much:
# 1. Increase test interval
# 2. Check for multiple instances running
ps aux | grep bandwidth

# Kill duplicate processes
killall python3
sudo systemctl restart bandwidth-monitor.service
```

### SD Card Full

```bash
# Check disk space
df -h

# Clean up old logs
journalctl --vacuum-time=7d

# Check database size
ls -lh ~/led-sign-project/bandwidth_data.db

# Optional: Archive old data and start fresh
mv bandwidth_data.db bandwidth_data_old.db
```

---

## Optimization Tips

### Reduce Power Consumption

```bash
# Disable HDMI (saves ~25mA)
sudo /usr/bin/tvservice -o

# Disable Bluetooth (not needed for monitoring)
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt

# Disable WiFi if using Ethernet
echo "dtoverlay=disable-wifi" | sudo tee -a /boot/config.txt

# Reboot to apply
sudo reboot
```

### Improve Performance

```bash
# Increase swap (helps with memory)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change: CONF_SWAPSIZE=512
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Set GPU memory low (we don't use GPU)
sudo raspi-config
# Performance Options → GPU Memory → 16
```

### Scheduled Reboots (Optional)

Reboot weekly to clear memory:

```bash
sudo crontab -e

# Add line to reboot every Sunday at 3am
0 3 * * 0 /sbin/shutdown -r now
```

### Log Rotation

Prevent logs from filling disk:

```bash
sudo nano /etc/logrotate.d/bandwidth-monitor
```

Add:

```
/home/pi/led-sign-project/bandwidth_monitor.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Monitor Pi Health

Create health check script:

```bash
nano ~/check_health.sh
```

```bash
#!/bin/bash
echo "=== Pi Health Check ==="
echo "Temperature: $(vcgencmd measure_temp)"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "Memory: $(free -m | awk 'NR==2{printf "%s/%sMB (%.2f%%)", $3,$2,$3*100/$2 }')"
echo "Disk: $(df -h / | awk 'NR==2{printf "%s/%s (%s)", $3,$2,$5}')"
echo "Uptime: $(uptime -p)"
systemctl is-active --quiet bandwidth-monitor.service && echo "Monitor: ✓ Running" || echo "Monitor: ✗ Stopped"
systemctl is-active --quiet bandwidth-dashboard.service && echo "Dashboard: ✓ Running" || echo "Dashboard: ✗ Stopped"
```

```bash
chmod +x ~/check_health.sh
./check_health.sh
```

---

## Quick Reference Commands

```bash
# Check status of everything
sudo systemctl status bandwidth-monitor.service bandwidth-dashboard.service

# View live monitoring
journalctl -u bandwidth-monitor.service -f

# Run manual test
python3 ~/led-sign-project/bandwidth_monitor.py --once

# View recent stats
python3 ~/led-sign-project/bandwidth_monitor.py --stats 24

# Restart everything
sudo systemctl restart bandwidth-monitor.service bandwidth-dashboard.service

# Check network
ip addr show
iwconfig wlan0  # WiFi
sudo ethtool eth0  # Ethernet

# Check Pi health
vcgencmd measure_temp
htop

# Access dashboard
http://bandwidth-monitor.local:5001
```

---

## Getting the Best Results

### For Detecting Xfinity Throttling

1. **Use Ethernet adapter** - essential for testing 800+ Mbps
2. **Run for 48+ hours** - captures patterns
3. **Monitor peak hours** - 6pm-11pm weekdays
4. **Document results** - take screenshots of dashboard
5. **Compare to plan** - you're paying for Gigabit

### Expected Results

**With Ethernet (Gigabit adapter):**
- Download: 800-950 Mbps (typical Xfinity Gigabit)
- Upload: 35-45 Mbps (Xfinity asymmetric)
- Ping: 10-20ms to nearby servers

**With WiFi (Pi Zero 2W built-in):**
- Download: 20-40 Mbps (WiFi limitation)
- Upload: 20-40 Mbps
- Ping: 15-30ms

### Red Flags for Throttling

- Speed drops at consistent times daily
- Gradual degradation over hours
- Speed recovers after router reboot
- Pattern changes on weekends vs weekdays

---

## Support & Resources

**Project Documentation:**
- `BANDWIDTH_MONITOR_README.md` - General usage
- `PI_ZERO_2W_GUIDE.md` - This guide

**Raspberry Pi Resources:**
- [Official Documentation](https://www.raspberrypi.com/documentation/)
- [Forums](https://forums.raspberrypi.com/)

**Speed Testing:**
- [Speedtest.net](https://www.speedtest.net/)
- [Fast.com](https://fast.com/) - Netflix's tester

**Check Service Status Anytime:**
```bash
ssh pi@bandwidth-monitor.local
sudo systemctl status bandwidth-monitor.service
```

---

**Happy monitoring! You'll have hard evidence if Xfinity is throttling your connection.**
