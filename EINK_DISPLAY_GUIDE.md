# E-Ink Display Setup for Bandwidth Monitor

Add a low-power, always-visible e-ink display to show your Xfinity bandwidth speeds in real-time!

## Why E-Ink?

- **Low Power**: Uses power only when updating (perfect for 24/7 operation)
- **Always Visible**: No backlight needed, readable in direct sunlight
- **Perfect for Pi Zero 2W**: Minimal resource usage
- **No Screen Burn**: Unlike OLED, e-ink won't burn in
- **Clean Look**: Professional appearance, great for wall-mounting

---

## Recommended E-Ink Displays

### Option 1: Waveshare 2.13" (Best for Pi Zero 2W)

**Specs:**
- Size: 2.13 inch
- Resolution: 250x122 pixels
- Price: ~$15-20
- Perfect for: Compact setup, desk mounting

**What fits:**
- Current download/upload speed
- Ping
- Alert status
- Last update time
- Threshold indicator

### Option 2: Waveshare 2.9"

**Specs:**
- Size: 2.9 inch
- Resolution: 296x128 pixels
- Price: ~$20-25
- Perfect for: More readable, same compact size

### Option 3: Waveshare 4.2"

**Specs:**
- Size: 4.2 inch
- Resolution: 400x300 pixels
- Price: ~$30-35
- Perfect for: Wall mounting, 24h statistics

**What fits:**
- Everything from smaller displays PLUS:
- 24-hour statistics
- Average/min/max speeds
- Alert count

### Option 4: Waveshare 7.5"

**Specs:**
- Size: 7.5 inch
- Resolution: 800x480 pixels
- Price: ~$60-80
- Perfect for: Large wall display, control center

**What fits:**
- Full statistics
- Graphs (if custom coded)
- Multiple data points

---

## Hardware Connection

### Waveshare E-Paper HAT Connection

E-ink displays connect to Pi Zero 2W via GPIO pins (SPI interface).

**GPIO Pin Connections:**

| E-Ink HAT Pin | Pi GPIO Pin | Function |
|---------------|-------------|----------|
| VCC | 3.3V (Pin 1) | Power |
| GND | GND (Pin 6) | Ground |
| DIN | GPIO 10 (MOSI) | Data In |
| CLK | GPIO 11 (SCLK) | Clock |
| CS | GPIO 8 (CE0) | Chip Select |
| DC | GPIO 25 | Data/Command |
| RST | GPIO 17 | Reset |
| BUSY | GPIO 24 | Busy |

**Most Waveshare HATs fit directly on GPIO header!**

### Physical Setup Options

**Option A: Direct Mount**
- E-Paper HAT sits directly on GPIO pins
- Most compact
- Pi stacks under display

**Option B: Ribbon Cable**
- Use GPIO ribbon cable extension
- Separate Pi from display
- Better for wall-mounting display

**Option C: HAT with Mounting Holes**
- Some HATs include standoffs
- Professional appearance
- Can mount in custom enclosure

---

## Software Installation

### Step 1: Run Pi Zero 2W Setup

If you haven't already:

```bash
cd ~/led-sign-project
./setup_pi_zero_2w.sh
```

### Step 2: Install E-Ink Drivers

```bash
cd ~/led-sign-project
chmod +x install_eink_drivers.sh
./install_eink_drivers.sh
```

This will:
- Install system dependencies (Pillow, numpy, SPI)
- Enable SPI interface
- Download Waveshare e-Paper library
- Install fonts
- Test display connection

**Note:** You'll need to reboot after enabling SPI (script will prompt)

### Step 3: Connect Hardware

1. Power off Pi: `sudo shutdown -h now`
2. Connect e-ink HAT to GPIO pins
3. Power back on

### Step 4: Test Display

```bash
cd ~/led-sign-project

# Generate test image (doesn't need hardware)
python3 bandwidth_eink_display.py --test --size 2.13

# View test image
# (Transfer eink_test_2.13.png to your computer to preview)

# Test with actual hardware
python3 bandwidth_eink_display.py --size 2.13
```

**Display Sizes:**
- Use `--size 2.13` for 2.13"
- Use `--size 2.9` for 2.9"
- Use `--size 4.2` for 4.2"
- Use `--size 7.5` for 7.5"

### Step 5: Set Up Auto-Start Service

```bash
# Create service (replace 2.13 with your display size)
sudo cp bandwidth-eink.service.template /etc/systemd/system/bandwidth-eink.service

# Edit to set your display size
sudo nano /etc/systemd/system/bandwidth-eink.service

# Change this line:
# ExecStart=/usr/bin/python3 /home/pi/led-sign-project/bandwidth_eink_display.py --size 2.13
# To your size: 2.9, 4.2, or 7.5

# Save and exit (Ctrl+O, Enter, Ctrl+X)

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable bandwidth-eink.service
sudo systemctl start bandwidth-eink.service

# Check status
sudo systemctl status bandwidth-eink.service
```

---

## What The Display Shows

### Small Displays (2.13", 2.9")

```
┌─────────────────────────┐
│ XFINITY BANDWIDTH       │
│                         │
│ ↓ Download              │
│   856 Mbps              │
│                         │
│ ↑ 42 Mbps  •  Ping: 12ms│
│                         │
│ Last test: Dec 15 2:35PM│
│                         │
│ Threshold: 800 Mbps     │
└─────────────────────────┘
```

**If below threshold:**
```
┌─────────────────────────┐
│ XFINITY BANDWIDTH       │
│ ⚠ BELOW 800 MBPS        │
│                         │
│ ↓ Download              │
│   742 Mbps              │
│                         │
│ ↑ 38 Mbps  •  Ping: 15ms│
└─────────────────────────┘
```

### Large Displays (4.2", 7.5")

Includes 24-hour statistics:

```
┌──────────────────────────────────┐
│ XFINITY BANDWIDTH                │
│                                  │
│ ↓ Download                       │
│   856 Mbps                       │
│                                  │
│ ↑ 42 Mbps  •  Ping: 12 ms       │
│ Last test: Dec 15 2:35 PM        │
│                                  │
│ ─────────────────────────────    │
│ 24 HOUR STATS                    │
│ Avg: 842.5 Mbps                  │
│ Min: 798.2 Mbps                  │
│ Max: 923.1 Mbps                  │
│ Tests: 48                        │
│ ⚠ Alerts: 2                      │
│                                  │
│ Threshold: 800 Mbps              │
└──────────────────────────────────┘
```

---

## Configuration

### Update Interval

Default: 300 seconds (5 minutes) - matches speed test interval

Change interval:

```bash
# Edit service file
sudo nano /etc/systemd/system/bandwidth-eink.service

# Change --interval value:
ExecStart=/usr/bin/python3 /home/pi/led-sign-project/bandwidth_eink_display.py --size 2.13 --interval 600

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart bandwidth-eink.service
```

### Threshold

Default: 800 Mbps

Change threshold:

```bash
# Edit service file
sudo nano /etc/systemd/system/bandwidth-eink.service

# Change --threshold value:
ExecStart=/usr/bin/python3 /home/pi/led-sign-project/bandwidth_eink_display.py --size 2.13 --threshold 900

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart bandwidth-eink.service
```

---

## Management Commands

```bash
# Check if e-ink display is running
sudo systemctl status bandwidth-eink.service

# View logs
journalctl -u bandwidth-eink.service -f

# Restart display
sudo systemctl restart bandwidth-eink.service

# Stop display
sudo systemctl stop bandwidth-eink.service

# Start display
sudo systemctl start bandwidth-eink.service

# Disable auto-start
sudo systemctl disable bandwidth-eink.service

# Enable auto-start
sudo systemctl enable bandwidth-eink.service
```

### Manual Test

```bash
cd ~/led-sign-project

# Run manually (Ctrl+C to stop)
python3 bandwidth_eink_display.py --size 2.13

# Generate test image without hardware
python3 bandwidth_eink_display.py --test --size 2.13
# Creates: eink_test_2.13.png
```

---

## Troubleshooting

### Display Not Working

**1. Check SPI is enabled:**

```bash
lsmod | grep spi
# Should show spi_bcm2835

# If not:
sudo raspi-config
# Interface Options → SPI → Enable
# Reboot
```

**2. Check display connection:**

```bash
# View GPIO usage
gpio readall

# Check for SPI device
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

**3. Check wiring:**

- Ensure HAT is fully seated on GPIO pins
- Verify ribbon cable connections
- Check for bent pins

**4. Test with Waveshare examples:**

```bash
cd ~/led-sign-project/lib/e-Paper/RaspberryPi_JetsonNano/python/examples
python3 epd_2in13_V3_test.py  # Change to your model
```

### Import Errors

```bash
# Reinstall drivers
cd ~/led-sign-project
./install_eink_drivers.sh

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Manually test import
python3 -c "import sys; sys.path.append('./lib'); from waveshare_epd import epd2in13_V3"
```

### Display Shows Garbage

- Wrong display size selected
- Check `--size` parameter matches hardware

### Service Won't Start

```bash
# Check service status
sudo systemctl status bandwidth-eink.service

# View detailed logs
journalctl -u bandwidth-eink.service -n 50

# Check file permissions
ls -l ~/led-sign-project/bandwidth_eink_display.py

# Make executable
chmod +x ~/led-sign-project/bandwidth_eink_display.py

# Test manually first
cd ~/led-sign-project
python3 bandwidth_eink_display.py --size 2.13
```

### Display Won't Update

```bash
# Check bandwidth monitor is running
sudo systemctl status bandwidth-monitor.service

# Check database exists
ls -lh ~/led-sign-project/bandwidth_data.db

# Run test to populate database
python3 ~/led-sign-project/bandwidth_monitor.py --once

# Restart e-ink display
sudo systemctl restart bandwidth-eink.service
```

---

## Power Consumption

E-ink displays are incredibly power efficient:

| Display Size | Update Power | Idle Power | Notes |
|--------------|-------------|------------|-------|
| 2.13" | ~40mA | <1mA | Updates in ~2 seconds |
| 2.9" | ~50mA | <1mA | Updates in ~2 seconds |
| 4.2" | ~80mA | <1mA | Updates in ~3 seconds |
| 7.5" | ~120mA | <1mA | Updates in ~5 seconds |

**Pi Zero 2W Total Power:**
- Idle: ~120mA
- With WiFi: ~180mA
- With Ethernet: ~200mA
- E-ink update: +40-120mA for 2-5 seconds

**24-hour power (5-minute update interval):**
- Pi base: 0.9-1.2W continuously
- E-ink: Negligible (only during brief updates)
- **Total: ~1.2W average**

**Cost:** ~$0.10/month at $0.12/kWh

---

## Physical Mounting Ideas

### Option 1: Desk Stand

- 3D print custom stand
- Use adhesive standoffs
- Lean against wall

### Option 2: Wall Mount

- Picture frame mount
- 3M command strips
- Floating shelf

### Option 3: Enclosure

- Custom 3D printed case
- Laser-cut acrylic case
- Shadow box frame

### Option 4: Multi-Display Dashboard

- Mount multiple stats displays
- Speed + Weather + Calendar
- Control center aesthetic

---

## Shopping List

### For 2.13" Display Setup (Recommended)

| Item | Price | Link/Notes |
|------|-------|------------|
| Waveshare 2.13" V3 HAT | $15-20 | Amazon, Waveshare official |
| Pi Zero 2W | $15 | If you don't have |
| MicroSD 16GB | $8 | If you don't have |
| Power Supply | $8 | If you don't have |
| USB Ethernet (optional) | $12 | For 800+ Mbps testing |
| Case/Mount (optional) | $5-15 | 3D print or purchase |

**Total:** $15-20 (display only) or $56-76 (complete kit)

---

## Advanced: Custom Display Layouts

The display script is open source! Customize the layout:

```bash
nano ~/led-sign-project/bandwidth_eink_display.py
```

Key function to modify:
- `create_display_image()` - Layout and content

Ideas:
- Add graph of last 24 hours
- Show upload prominently
- Custom alert messages
- ISP logo
- QR code to dashboard

---

## Quick Reference

```bash
# Install drivers
./install_eink_drivers.sh

# Test display
python3 bandwidth_eink_display.py --test --size 2.13

# Run manually
python3 bandwidth_eink_display.py --size 2.13

# Set up service
sudo cp bandwidth-eink.service.template /etc/systemd/system/bandwidth-eink.service
sudo nano /etc/systemd/system/bandwidth-eink.service  # Edit size
sudo systemctl daemon-reload
sudo systemctl enable bandwidth-eink.service
sudo systemctl start bandwidth-eink.service

# Check status
sudo systemctl status bandwidth-eink.service

# View logs
journalctl -u bandwidth-eink.service -f
```

---

## FAQ

**Q: Can I use other e-ink displays besides Waveshare?**
A: Waveshare is recommended as drivers are included. Other brands may require custom code.

**Q: Will it work with Pi 3/4/5?**
A: Yes! Works with all Raspberry Pi models with GPIO.

**Q: How often does it update?**
A: Default 5 minutes (matches speed test interval). Customizable.

**Q: Can I run this and the web dashboard together?**
A: Yes! They work perfectly together. E-ink for glance, web for details.

**Q: Does the e-ink screen wear out?**
A: No burn-in like OLED. Rated for millions of refreshes.

**Q: Can I add more information?**
A: Yes! Edit `bandwidth_eink_display.py` to customize layout.

---

## Support

**Check status:**
```bash
sudo systemctl status bandwidth-eink.service
```

**View logs:**
```bash
journalctl -u bandwidth-eink.service -f
```

**Test hardware:**
```bash
cd ~/led-sign-project/lib
python3 test_eink.py
```

---

**Enjoy your always-on bandwidth monitor! Perfect for catching Xfinity throttling at a glance.** 🖥️
