# Pi Zero 2W Bandwidth Monitor - Quick Start

Get your Pi Zero 2W monitoring Xfinity speeds in under 30 minutes!

## What You'll Need

### Hardware Shopping List

**Essential:**
- [x] Raspberry Pi Zero 2W ($15)
- [x] MicroSD card 16GB+ ($8)
- [x] USB power supply 5V 2.5A ($8)

**For 800+ Mbps Testing (Highly Recommended):**
- [ ] USB OTG cable/adapter ($5)
- [ ] USB Gigabit Ethernet adapter ($12-15)
  - UGREEN USB 2.0 to Ethernet (RTL8153)
  - Cable Matters USB to Gigabit Ethernet
  - TP-Link UE300
- [ ] Ethernet cable

**Total Cost: $48-56 for complete setup**

## Setup Steps

### 1. Prepare the SD Card (10 minutes)

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert microSD card into your computer
3. Open Pi Imager:
   - **OS**: Raspberry Pi OS Lite (64-bit)
   - **Storage**: Your SD card
   - Click **⚙️ Gear icon** for advanced:
     - Hostname: `bandwidth-monitor`
     - ✓ Enable SSH
     - Username: `pi`
     - Password: (your choice)
     - ✓ Configure WiFi: Enter your network details
     - Set timezone
   - Click **WRITE**

### 2. Boot the Pi (5 minutes)

1. Insert SD card into Pi Zero 2W
2. Connect power
3. Wait 60 seconds for first boot
4. From your computer, SSH in:
   ```bash
   ssh pi@bandwidth-monitor.local
   ```

### 3. Connect Hardware (5 minutes)

**Option A: Ethernet (Recommended for 800+ Mbps)**
```
Pi Zero 2W → USB OTG Adapter → USB Ethernet Adapter → Ethernet Cable → Router
```

**Option B: WiFi Only (20-40 Mbps max)**
```
Already configured during SD card setup
```

### 4. Run Automated Setup (10 minutes)

```bash
# Get the project files
cd ~
git clone https://github.com/YOUR_USERNAME/led-sign-project.git
cd led-sign-project

# Run setup script
chmod +x setup_pi_zero_2w.sh
./setup_pi_zero_2w.sh
```

The script will:
- ✓ Detect your Pi and network
- ✓ Install all dependencies
- ✓ Run initial speed test
- ✓ Set up auto-start services
- ✓ Configure monitoring

When prompted "Start monitoring services now?" → Type **y**

### 5. Access Dashboard (Right Now!)

From any device on your network, open browser:

```
http://bandwidth-monitor.local:5001
```

**Done!** You're now monitoring your Xfinity speeds 24/7.

---

## What Happens Next?

The Pi will automatically:
- Test your speed every 5 minutes
- Alert when speed drops below 800 Mbps
- Store all results in database
- Display trends on web dashboard
- Auto-start on boot

---

## Quick Commands

```bash
# SSH back into Pi anytime
ssh pi@bandwidth-monitor.local

# Check if monitoring is running
sudo systemctl status bandwidth-monitor.service

# View live monitoring
journalctl -u bandwidth-monitor.service -f

# Run manual test
python3 ~/led-sign-project/bandwidth_monitor.py --once

# View 24 hour stats
python3 ~/led-sign-project/bandwidth_monitor.py --stats 24

# Check network setup
~/led-sign-project/check_network_pi.sh

# Restart services
sudo systemctl restart bandwidth-monitor.service
sudo systemctl restart bandwidth-dashboard.service
```

---

## Understanding Results

### With Ethernet Adapter (Recommended)

**Normal Xfinity Gigabit:**
- Download: 800-950 Mbps ✓
- Upload: 35-45 Mbps
- Ping: 10-20ms

**Alert Triggers (Below 800 Mbps):**
- Possible throttling
- Network congestion
- Router issues
- Service problems

### With WiFi Only

**Normal WiFi (Pi Zero 2W):**
- Download: 20-40 Mbps
- Upload: 20-40 Mbps
- Ping: 15-30ms

**Note:** WiFi speeds are limited by Pi Zero 2W hardware, not your internet. Still useful for detecting patterns!

---

## Red Flags for Throttling

Monitor the dashboard for these patterns:

🚨 **Speed drops at same time daily** (e.g., every evening 7-10pm)
🚨 **Gradual degradation** over hours, then sudden recovery
🚨 **Weekday vs weekend patterns**
🚨 **Speed recovers after router reboot**

Take screenshots of your dashboard as evidence!

---

## Network Check

Run diagnostic script anytime:

```bash
cd ~/led-sign-project
./check_network_pi.sh
```

This shows:
- Network interface status
- Connection speed capability
- WiFi signal quality
- Internet connectivity
- Whether you can test 800+ Mbps

---

## Hardware Comparison

| Setup | Max Speed Test | Cost | Best For |
|-------|---------------|------|----------|
| **Pi + WiFi** | ~40 Mbps | $31 | WiFi monitoring, patterns |
| **Pi + Ethernet** | 1000 Mbps | $56 | Full Xfinity speed testing ✓ |

---

## Troubleshooting

### Can't SSH to Pi
```bash
# Try IP directly (check your router)
ssh pi@192.168.1.XXX

# Or reconnect to WiFi
```

### Dashboard Won't Load
```bash
# Check service
sudo systemctl status bandwidth-dashboard.service

# Restart it
sudo systemctl restart bandwidth-dashboard.service

# Try IP directly
http://192.168.1.XXX:5001
```

### Speed Tests Failing
```bash
# Test manually
python3 ~/led-sign-project/bandwidth_monitor.py --once

# Check logs
journalctl -u bandwidth-monitor.service -n 50
```

### Ethernet Not Detected
```bash
# Check USB devices
lsusb

# Check interfaces
ip link show

# Run network check
~/led-sign-project/check_network_pi.sh
```

---

## Need More Info?

📖 **Full Documentation:**
- `PI_ZERO_2W_GUIDE.md` - Complete setup guide
- `BANDWIDTH_MONITOR_README.md` - General usage

🛠️ **Helper Scripts:**
- `setup_pi_zero_2w.sh` - Automated setup
- `check_network_pi.sh` - Network diagnostic
- `setup_bandwidth_monitor.sh` - Generic setup

---

## Tips for Best Results

1. **Use Ethernet** - USB adapter required for 800+ Mbps testing
2. **Close to Router** - If using WiFi, minimize distance
3. **Let it Run** - Monitor for 48+ hours to see patterns
4. **Peak Hours** - Check evenings (6-11pm) when throttling is common
5. **Document Everything** - Screenshots for Xfinity support calls

---

## Support

**Check Status:**
```bash
ssh pi@bandwidth-monitor.local
sudo systemctl status bandwidth-monitor.service
```

**View Dashboard:**
```
http://bandwidth-monitor.local:5001
```

**Get Help:**
- Check troubleshooting section above
- Review logs: `journalctl -u bandwidth-monitor.service -f`
- Run diagnostic: `./check_network_pi.sh`

---

**You're all set! Your Pi Zero 2W is now watching Xfinity 24/7.**

Check the dashboard regularly for evidence of throttling. Good luck! 🚀
