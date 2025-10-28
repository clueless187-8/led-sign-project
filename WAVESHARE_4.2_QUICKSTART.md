# Waveshare 4.2" E-Ink Display - Quick Setup

Perfect choice! The 4.2" display shows full bandwidth data including 24-hour statistics.

## What You'll See on 4.2" Display

```
┌────────────────────────────────────────┐
│ XFINITY BANDWIDTH                      │
│                                        │
│ ↓ Download                             │
│   856 Mbps                             │
│                                        │
│ ↑ 42 Mbps  •  Ping: 12 ms             │
│ Last test: Dec 15 2:35 PM              │
│                                        │
│ ────────────────────────────────────   │
│ 24 HOUR STATS                          │
│ Avg: 842.5 Mbps                        │
│ Min: 798.2 Mbps                        │
│ Max: 923.1 Mbps                        │
│ Tests: 48                              │
│ ⚠ Alerts: 2                            │
│                                        │
│ Threshold: 800 Mbps                    │
└────────────────────────────────────────┘
```

**Resolution:** 400x300 pixels - plenty of room for detailed stats!

---

## Hardware Specs

**Waveshare 4.2" E-Paper Display:**
- **Size:** 4.2 inches
- **Resolution:** 400 x 300 pixels
- **Colors:** Black & White
- **Refresh Time:** ~4 seconds
- **Price:** ~$30-35
- **Interface:** SPI (fits on GPIO pins)
- **Power:** ~80mA during update, <1mA idle

---

## What You Need

### Hardware Shopping List

- [x] **Waveshare 4.2" E-Paper HAT** ($30-35)
  - Model: 4.2inch e-Paper Module
  - Make sure it's the HAT version (has GPIO connector)
  - Compatible with Pi Zero 2W

- [x] **Pi Zero 2W** (you already have)
- [x] **MicroSD Card** (you already have)
- [x] **Power Supply** (you already have)
- [x] **USB Ethernet Adapter** (recommended for 800+ Mbps testing)

**No additional cables needed!** The HAT plugs directly onto the GPIO pins.

---

## Physical Setup

### Mounting the Display

**Option 1: Stack Configuration**
```
┌─────────────┐
│  4.2" HAT   │ ← E-ink display on top
├─────────────┤
│ Pi Zero 2W  │ ← Pi in middle
├─────────────┤
│ Base/Stand  │ ← Optional 3D printed base
└─────────────┘
```

**Option 2: Wall Mount**
```
      Wall
       │
    ┌──┴──┐
    │ 4.2"│ ← Display visible
    └──┬──┘
       │
    Hidden: Pi Zero 2W behind
```

**Option 3: Desk Frame**
- Picture frame mount
- Angled stand
- Professional appearance

---

## Software Installation

### Step 1: Prepare Your Pi (If Not Done Already)

```bash
# Flash Raspberry Pi OS Lite to SD card
# Using Raspberry Pi Imager:
# - OS: Raspberry Pi OS Lite (64-bit)
# - Enable SSH
# - Set hostname: bandwidth-monitor
# - Configure WiFi
# - Set username: pi

# Boot Pi and SSH in
ssh pi@bandwidth-monitor.local
```

### Step 2: Get the Project Files

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/led-sign-project.git
cd led-sign-project
```

### Step 3: Run Pi Zero 2W Setup

```bash
chmod +x setup_pi_zero_2w.sh
./setup_pi_zero_2w.sh
```

This installs bandwidth monitoring (choose to start services when prompted).

### Step 4: Install E-Ink Drivers

```bash
chmod +x install_eink_drivers.sh
./install_eink_drivers.sh
```

**Important:** When it asks to reboot for SPI, say **YES**.

```bash
# After script completes, it will ask:
Reboot now? [y/N]: y
```

### Step 5: Connect Hardware

**After reboot:**

1. **Power off Pi:**
   ```bash
   sudo shutdown -h now
   ```

2. **Connect the 4.2" HAT:**
   - Align HAT GPIO pins with Pi GPIO header
   - Press firmly but gently
   - All 40 pins should connect

3. **Power back on**

### Step 6: Test the Display

```bash
# SSH back in
ssh pi@bandwidth-monitor.local
cd ~/led-sign-project

# Generate test image (preview without hardware)
python3 bandwidth_eink_display.py --test --size 4.2
# Creates: eink_test_4.2.png

# View the test image by downloading it:
# scp pi@bandwidth-monitor.local:~/led-sign-project/eink_test_4.2.png ./

# Test with actual hardware (this will update the display)
python3 bandwidth_eink_display.py --size 4.2
```

**You should see:**
- Display clears (white)
- New image appears with bandwidth data
- Takes about 4 seconds to update

**Press Ctrl+C to stop after verifying it works**

### Step 7: Set Up Auto-Start Service

```bash
# Create service file
sudo tee /etc/systemd/system/bandwidth-eink.service > /dev/null <<EOF
[Unit]
Description=Bandwidth Monitor E-Ink Display 4.2"
After=network-online.target bandwidth-monitor.service
Wants=network-online.target
Requires=bandwidth-monitor.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/led-sign-project
Environment="EINK_DISPLAY_SIZE=4.2"
ExecStart=/usr/bin/python3 /home/pi/led-sign-project/bandwidth_eink_display.py --size 4.2 --interval 300 --threshold 800
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable bandwidth-eink.service

# Start the service now
sudo systemctl start bandwidth-eink.service

# Check it's running
sudo systemctl status bandwidth-eink.service
```

**Done!** Your display will now update automatically every 5 minutes and start on boot.

---

## Verify Everything is Working

```bash
# Check all services are running
sudo systemctl status bandwidth-monitor.service
sudo systemctl status bandwidth-dashboard.service
sudo systemctl status bandwidth-eink.service

# View e-ink logs
journalctl -u bandwidth-eink.service -f

# Should show:
# "Updating display..."
# "Current speed: ↓XXX.X Mbps ↑XX.X Mbps"
# "Next update in 300 seconds..."
```

---

## What Gets Displayed

### Upper Section (Speed Data)
- **Main Title:** "XFINITY BANDWIDTH"
- **Alert Banner:** (if speed < 800 Mbps) "⚠ BELOW 800 MBPS"
- **Download Speed:** Large text, e.g., "856 Mbps"
- **Upload & Ping:** "↑ 42 Mbps  •  Ping: 12 ms"
- **Timestamp:** "Last test: Dec 15 2:35 PM"

### Lower Section (24h Statistics)
- **Average Download:** Rolling 24h average
- **Min Download:** Lowest speed in 24h
- **Max Download:** Highest speed in 24h
- **Total Tests:** Number of tests run
- **Alerts Count:** Times speed dropped below 800 Mbps

### Footer
- **Threshold Indicator:** "Threshold: 800 Mbps"

---

## Configuration Options

### Change Update Interval

Default: 300 seconds (5 minutes) - matches speed test frequency

To change:

```bash
sudo nano /etc/systemd/system/bandwidth-eink.service

# Change this line:
ExecStart=/usr/bin/python3 /home/pi/led-sign-project/bandwidth_eink_display.py --size 4.2 --interval 600 --threshold 800
#                                                                                           ^^^^ 10 minutes

# Save and restart
sudo systemctl daemon-reload
sudo systemctl restart bandwidth-eink.service
```

### Change Threshold

Default: 800 Mbps

To change to 900 Mbps:

```bash
sudo nano /etc/systemd/system/bandwidth-eink.service

# Change --threshold value:
ExecStart=/usr/bin/python3 /home/pi/led-sign-project/bandwidth_eink_display.py --size 4.2 --interval 300 --threshold 900

# Save and restart
sudo systemctl daemon-reload
sudo systemctl restart bandwidth-eink.service
```

---

## Troubleshooting

### Display Not Updating

```bash
# Check service status
sudo systemctl status bandwidth-eink.service

# View recent logs
journalctl -u bandwidth-eink.service -n 50

# Restart service
sudo systemctl restart bandwidth-eink.service
```

### "No data available" Shows

```bash
# Make sure bandwidth monitor has run at least once
python3 ~/led-sign-project/bandwidth_monitor.py --once

# Check database exists
ls -lh ~/led-sign-project/bandwidth_data.db

# Restart e-ink display
sudo systemctl restart bandwidth-eink.service
```

### Display Shows Garbled Image

```bash
# Wrong size parameter - verify you're using 4.2
sudo nano /etc/systemd/system/bandwidth-eink.service

# Should say --size 4.2 (not 2.13 or other)

# Restart after fixing
sudo systemctl daemon-reload
sudo systemctl restart bandwidth-eink.service
```

### SPI Not Enabled

```bash
# Check SPI is loaded
lsmod | grep spi

# If nothing shows, enable it:
sudo raspi-config
# Interface Options → SPI → Enable → Reboot

# Verify SPI devices exist
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

### Display Partially Works

```bash
# Test Waveshare examples
cd ~/led-sign-project/lib/e-Paper/RaspberryPi_JetsonNano/python/examples
python3 epd_4in2_test.py

# If that works, issue is with bandwidth script
# View detailed errors:
journalctl -u bandwidth-eink.service -n 100
```

---

## Power Consumption

**4.2" E-Ink Display:**
- **During Update:** ~80mA for 4 seconds
- **Idle:** <1mA (almost nothing!)

**Complete System (Pi + Display):**
- **Pi Zero 2W Base:** ~120mA
- **With WiFi:** ~180mA
- **With Ethernet:** ~200mA
- **During Update:** +80mA for 4 seconds

**24-Hour Power Usage:**
- Updates: 288 times/day × 4 seconds × 280mA = 0.32 Wh
- Idle: 200mA × 24h = 4.8 Wh
- **Total:** ~5 Wh/day = 0.15 kWh/month

**Monthly Cost:** ~$0.02/month at $0.12/kWh

**Incredibly cheap to run 24/7!**

---

## Maintenance

### View Logs Anytime

```bash
# Real-time monitoring
journalctl -u bandwidth-eink.service -f

# Last 50 entries
journalctl -u bandwidth-eink.service -n 50

# Today only
journalctl -u bandwidth-eink.service --since today
```

### Restart Display

```bash
sudo systemctl restart bandwidth-eink.service
```

### Stop Display Temporarily

```bash
# Stop
sudo systemctl stop bandwidth-eink.service

# Start again
sudo systemctl start bandwidth-eink.service
```

### Update Display Code

```bash
cd ~/led-sign-project
git pull

# Restart service to use new code
sudo systemctl restart bandwidth-eink.service
```

---

## Mounting Ideas for 4.2"

### Wall Mount Options

**1. Picture Frame**
- 5x7" frame fits 4.2" display perfectly
- Remove glass, mount display in frame
- Hang on wall

**2. Floating Mount**
- 3M Command strips
- Mount directly to wall
- Clean, minimal look

**3. Shadow Box**
- Deep frame with space for Pi behind display
- Everything hidden
- Professional appearance

### Desk Mount Options

**1. Angled Stand**
- 3D print custom stand
- 30-45° angle for easy viewing
- Pi mounts underneath

**2. Easel Style**
- Display stands like picture frame
- Adjustable angle
- Easy to move

**3. Monitor Stand**
- Small monitor riser
- Display sits on top
- Pi underneath

---

## Complete System Overview

Once everything is running:

**Services Running:**
1. **bandwidth-monitor.service** - Tests speed every 5 min
2. **bandwidth-dashboard.service** - Web dashboard on port 5001
3. **bandwidth-eink.service** - Updates e-ink display every 5 min

**Access Points:**
- **E-Ink Display:** Physical display showing current data
- **Web Dashboard:** http://bandwidth-monitor.local:5001
- **Database:** ~/led-sign-project/bandwidth_data.db
- **Logs:** `journalctl -u bandwidth-*.service`

---

## Quick Commands Reference

```bash
# Check all services
sudo systemctl status bandwidth-*

# View e-ink logs
journalctl -u bandwidth-eink.service -f

# Restart e-ink display
sudo systemctl restart bandwidth-eink.service

# Test display manually
python3 ~/led-sign-project/bandwidth_eink_display.py --size 4.2

# Generate preview image
python3 ~/led-sign-project/bandwidth_eink_display.py --test --size 4.2

# Run speed test now
python3 ~/led-sign-project/bandwidth_monitor.py --once

# View web dashboard
# Open browser: http://bandwidth-monitor.local:5001
```

---

## Shopping Checklist

- [ ] Waveshare 4.2" E-Paper HAT (~$30-35)
- [ ] Optional: USB Ethernet adapter for 800+ Mbps testing ($12-15)
- [ ] Optional: Picture frame or stand for mounting ($5-15)
- [ ] Optional: Case for Pi Zero 2W ($5-10)

**Total:** $30-70 depending on options

---

## Expected Timeline

1. **Order Display:** 2-7 days shipping
2. **Receive & Unbox:** 5 minutes
3. **Flash Pi (if new):** 15 minutes
4. **Run setup scripts:** 20 minutes
5. **Connect display:** 2 minutes
6. **Test & configure:** 10 minutes

**Total Setup Time:** ~1 hour from start to finish!

---

## Support

**Issues? Check:**

1. All services running: `sudo systemctl status bandwidth-*`
2. SPI enabled: `ls /dev/spi*`
3. Display connected: Check GPIO connection
4. View logs: `journalctl -u bandwidth-eink.service -f`

**Still stuck?**
- Check EINK_DISPLAY_GUIDE.md for detailed troubleshooting
- Run: `~/led-sign-project/check_network_pi.sh` for diagnostics

---

**Enjoy your 4.2" bandwidth monitor! Perfect size for wall mounting and seeing all your stats at a glance!** 🎯
