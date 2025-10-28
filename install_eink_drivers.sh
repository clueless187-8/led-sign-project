#!/bin/bash
# Install Waveshare e-Paper HAT drivers for Raspberry Pi
# Supports multiple e-ink display sizes

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Waveshare E-Ink Display Driver Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo -e "${RED}Error: Not running on Raspberry Pi${NC}"
    exit 1
fi

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-pil python3-numpy git

echo ""
echo "Installing Python dependencies..."
pip3 install Pillow numpy spidev RPi.GPIO

echo ""
echo "Enabling SPI interface..."
# Enable SPI if not already enabled
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo -e "${GREEN}✓ SPI enabled (reboot required)${NC}"
    REBOOT_NEEDED=true
else
    echo -e "${GREEN}✓ SPI already enabled${NC}"
fi

echo ""
echo "Downloading Waveshare e-Paper library..."

# Create lib directory
mkdir -p ~/led-sign-project/lib
cd ~/led-sign-project/lib

# Clone Waveshare e-Paper library
if [ -d "e-Paper" ]; then
    echo "e-Paper library already exists, updating..."
    cd e-Paper
    git pull
    cd ..
else
    git clone https://github.com/waveshare/e-Paper.git
fi

# Copy Python library to project
if [ -d "e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd" ]; then
    cp -r e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd .
    echo -e "${GREEN}✓ Waveshare library installed${NC}"
else
    echo -e "${RED}Error: Waveshare library not found in expected location${NC}"
    exit 1
fi

# Copy font files
if [ -d "e-Paper/RaspberryPi_JetsonNano/python/pic" ]; then
    cp -r e-Paper/RaspberryPi_JetsonNano/python/pic ../fonts 2>/dev/null || true
fi

echo ""
echo "Installing additional fonts..."
sudo apt install -y fonts-dejavu fonts-liberation ttf-bitstream-vera

echo ""
echo "Testing e-ink display connection..."

# Create test script
cat > test_eink.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.append('./lib')

try:
    from waveshare_epd import epd2in13_V3
    print("✓ E-ink driver import successful")
    print("Attempting to initialize display...")

    epd = epd2in13_V3.EPD()
    epd.init()
    print("✓ Display initialized successfully!")
    epd.Clear()
    print("✓ Display cleared")
    epd.sleep()
    print("✓ Display put to sleep")
    print("\n✓✓✓ E-ink display is working! ✓✓✓\n")
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nPossible issues:")
    print("  • Display not connected properly")
    print("  • SPI not enabled (reboot required)")
    print("  • Wrong display model")
    sys.exit(1)
EOF

chmod +x test_eink.py

cd ~/led-sign-project

# Ask user to test
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Hardware Check${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Is your e-ink display connected to the Pi GPIO pins?"
read -p "Test display now? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Testing display..."
    cd lib
    python3 test_eink.py
    cd ..
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$REBOOT_NEEDED" = true ]; then
    echo -e "${YELLOW}⚠ REBOOT REQUIRED to enable SPI${NC}"
    echo ""
    read -p "Reboot now? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    else
        echo "Remember to reboot before using the e-ink display!"
    fi
fi

echo ""
echo "Next steps:"
echo ""
echo "1. Make sure your e-ink display is connected to GPIO"
echo ""
echo "2. Test the bandwidth display:"
echo "   ${GREEN}python3 bandwidth_eink_display.py --test --size 2.13${NC}"
echo ""
echo "3. Run the display:"
echo "   ${GREEN}python3 bandwidth_eink_display.py --size 2.13${NC}"
echo ""
echo "4. Set up as a service:"
echo "   ${GREEN}sudo systemctl enable bandwidth-eink.service${NC}"
echo "   ${GREEN}sudo systemctl start bandwidth-eink.service${NC}"
echo ""
echo "Supported display sizes: 2.13, 2.9, 4.2, 7.5"
echo ""
