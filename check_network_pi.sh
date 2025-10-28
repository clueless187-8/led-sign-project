#!/bin/bash
# Network Detection and Speed Capability Check for Pi Zero 2W
# Helps determine if your setup can test 800+ Mbps speeds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Network Configuration & Capability Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running on Pi
if [ -f /proc/device-tree/model ]; then
    PI_MODEL=$(cat /proc/device-tree/model)
    echo -e "${GREEN}Device:${NC} $PI_MODEL"
else
    echo -e "${YELLOW}Note: Not running on Raspberry Pi${NC}"
fi

echo ""
echo "━━━ Network Interfaces ━━━"
echo ""

HAS_ETH=false
HAS_WIFI=false
CAN_TEST_GIGABIT=false

# Check Ethernet
if [ -d /sys/class/net/eth0 ]; then
    HAS_ETH=true
    ETH_STATE=$(cat /sys/class/net/eth0/operstate 2>/dev/null || echo "unknown")

    if [ "$ETH_STATE" = "up" ]; then
        echo -e "${GREEN}✓ Ethernet (eth0): CONNECTED${NC}"

        # Get IP address
        ETH_IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
        if [ -n "$ETH_IP" ]; then
            echo "  IP Address: $ETH_IP"
        fi

        # Check speed
        if command -v ethtool &> /dev/null; then
            ETH_SPEED=$(ethtool eth0 2>/dev/null | grep "Speed:" | awk '{print $2}')
            ETH_DUPLEX=$(ethtool eth0 2>/dev/null | grep "Duplex:" | awk '{print $2}')

            if [ -n "$ETH_SPEED" ]; then
                echo "  Speed: $ETH_SPEED"
                echo "  Duplex: $ETH_DUPLEX"

                # Check if Gigabit
                if [[ "$ETH_SPEED" == *"1000"* ]]; then
                    echo -e "  ${GREEN}✓ Gigabit capable - can test 800+ Mbps${NC}"
                    CAN_TEST_GIGABIT=true
                elif [[ "$ETH_SPEED" == *"100"* ]]; then
                    echo -e "  ${YELLOW}⚠ 100 Mbps link - limited to ~95 Mbps max${NC}"
                else
                    echo -e "  ${YELLOW}⚠ Speed: $ETH_SPEED${NC}"
                fi
            fi
        else
            echo -e "  ${YELLOW}Install ethtool for speed info: sudo apt install ethtool${NC}"
        fi

        # Check USB devices for Ethernet adapter
        if command -v lsusb &> /dev/null; then
            USB_ETH=$(lsusb | grep -iE "ethernet|network")
            if [ -n "$USB_ETH" ]; then
                echo "  Adapter: $USB_ETH"
            fi
        fi
    else
        echo -e "${YELLOW}⚠ Ethernet (eth0): Interface exists but not connected${NC}"
        echo "  State: $ETH_STATE"
    fi
else
    echo -e "${RED}✗ Ethernet (eth0): No Ethernet adapter detected${NC}"
fi

echo ""

# Check WiFi
if [ -d /sys/class/net/wlan0 ]; then
    HAS_WIFI=true
    WIFI_STATE=$(cat /sys/class/net/wlan0/operstate 2>/dev/null || echo "unknown")

    if [ "$WIFI_STATE" = "up" ]; then
        echo -e "${GREEN}✓ WiFi (wlan0): CONNECTED${NC}"

        # Get SSID
        if command -v iwgetid &> /dev/null; then
            WIFI_SSID=$(iwgetid -r 2>/dev/null)
            if [ -n "$WIFI_SSID" ]; then
                echo "  SSID: $WIFI_SSID"
            fi
        fi

        # Get IP
        WIFI_IP=$(ip -4 addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
        if [ -n "$WIFI_IP" ]; then
            echo "  IP Address: $WIFI_IP"
        fi

        # Get signal quality
        if command -v iwconfig &> /dev/null; then
            WIFI_QUALITY=$(iwconfig wlan0 2>/dev/null | grep "Link Quality" | awk -F'[=/]' '{print $2"/"$3}')
            if [ -n "$WIFI_QUALITY" ]; then
                WIFI_PERCENT=$(iwconfig wlan0 2>/dev/null | grep "Link Quality" | awk -F'[=/]' '{print int($2/$3*100)}')
                echo "  Signal Quality: $WIFI_QUALITY ($WIFI_PERCENT%)"

                if [ "$WIFI_PERCENT" -ge 80 ]; then
                    echo -e "  ${GREEN}✓ Excellent signal${NC}"
                elif [ "$WIFI_PERCENT" -ge 60 ]; then
                    echo -e "  ${GREEN}✓ Good signal${NC}"
                elif [ "$WIFI_PERCENT" -ge 40 ]; then
                    echo -e "  ${YELLOW}⚠ Fair signal - move closer to router${NC}"
                else
                    echo -e "  ${RED}✗ Weak signal - move closer to router${NC}"
                fi
            fi

            # Power management
            WIFI_PM=$(iwconfig wlan0 2>/dev/null | grep "Power Management" | awk -F':' '{print $2}')
            if [[ "$WIFI_PM" == *"on"* ]]; then
                echo -e "  ${YELLOW}⚠ Power management: ON (may affect consistency)${NC}"
                echo "    Disable with: sudo iw dev wlan0 set power_save off"
            fi
        fi

        # WiFi speed limitation
        echo -e "  ${YELLOW}⚠ Pi Zero 2W WiFi typically limited to 20-40 Mbps${NC}"
        echo "    Use Ethernet adapter for testing 800+ Mbps"
    else
        echo -e "${YELLOW}⚠ WiFi (wlan0): Available but not connected${NC}"
        echo "  State: $WIFI_STATE"
    fi
else
    echo -e "${RED}✗ WiFi (wlan0): Not available${NC}"
fi

echo ""
echo "━━━ Network Connectivity Test ━━━"
echo ""

# Ping test
echo -n "Internet connectivity: "
if ping -c 1 -W 2 8.8.8.8 &> /dev/null; then
    echo -e "${GREEN}✓ Connected${NC}"

    # DNS test
    echo -n "DNS resolution: "
    if nslookup google.com &> /dev/null; then
        echo -e "${GREEN}✓ Working${NC}"
    else
        echo -e "${RED}✗ DNS issues${NC}"
    fi

    # Test speedtest.net connectivity
    echo -n "Speedtest.net access: "
    if curl -s --max-time 5 https://www.speedtest.net > /dev/null; then
        echo -e "${GREEN}✓ Reachable${NC}"
    else
        echo -e "${YELLOW}⚠ May have issues${NC}"
    fi
else
    echo -e "${RED}✗ No internet connection${NC}"
fi

echo ""
echo "━━━ Speed Test Capability Assessment ━━━"
echo ""

if [ "$CAN_TEST_GIGABIT" = true ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ READY FOR XFINITY 800 MBPS MONITORING${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Your setup can test full Gigabit speeds"
    echo "Ethernet connection is properly configured"
    echo ""
elif [ "$HAS_ETH" = true ] && [ "$ETH_STATE" = "up" ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠ LIMITED ETHERNET CAPABILITY${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Ethernet is connected but may not support Gigabit speeds"
    echo "Check your adapter specifications"
    echo ""
elif [ "$HAS_WIFI" = true ] && [ "$WIFI_STATE" = "up" ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠ WIFI-ONLY CONFIGURATION${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Current setup: WiFi only"
    echo "Expected max speed: ~20-40 Mbps"
    echo ""
    echo -e "${BLUE}To test full Xfinity speeds (800+ Mbps), you need:${NC}"
    echo "  1. USB OTG cable/adapter (~$5)"
    echo "  2. USB Gigabit Ethernet adapter (~$10-15)"
    echo "  3. Ethernet cable to router"
    echo ""
    echo "Recommended adapters:"
    echo "  • UGREEN USB 2.0 to Ethernet (RTL8153 chipset)"
    echo "  • Cable Matters USB to Gigabit Ethernet"
    echo "  • TP-Link UE300"
    echo ""
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ NO NETWORK CONNECTION${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "No active network connection detected"
    echo "Please configure WiFi or connect Ethernet"
    echo ""
fi

echo "━━━ Recommendations ━━━"
echo ""

if [ "$CAN_TEST_GIGABIT" = true ]; then
    echo "✓ Your setup is optimal for monitoring"
    echo "✓ Run: python3 bandwidth_monitor.py --once"
    echo "✓ Expected speeds: 800-950 Mbps download"
elif [ "$HAS_ETH" = true ] && [ "$ETH_STATE" = "up" ]; then
    echo "• Verify your Ethernet adapter supports Gigabit"
    echo "• Check cable quality (Cat5e or Cat6)"
    echo "• Test speed: python3 bandwidth_monitor.py --once"
elif [ "$HAS_WIFI" = true ] && [ "$WIFI_STATE" = "up" ]; then
    echo "• WiFi monitoring will show WiFi performance, not full internet speed"
    echo "• Purchase USB Ethernet adapter for accurate Xfinity speed testing"
    echo "• WiFi is still useful for detecting patterns and relative changes"
else
    echo "• Connect to network first (WiFi or Ethernet)"
    echo "• Run this script again after connecting"
fi

echo ""
echo "━━━ System Information ━━━"
echo ""

# Temperature
if command -v vcgencmd &> /dev/null; then
    TEMP=$(vcgencmd measure_temp | awk -F'=' '{print $2}')
    echo "Temperature: $TEMP"
fi

# Memory
MEM_USED=$(free -m | awk 'NR==2{printf "%sMB", $3}')
MEM_TOTAL=$(free -m | awk 'NR==2{printf "%sMB", $2}')
MEM_PERCENT=$(free | awk 'NR==2{printf "%.0f%%", $3*100/$2}')
echo "Memory: $MEM_USED / $MEM_TOTAL ($MEM_PERCENT used)"

# Disk
DISK_USED=$(df -h / | awk 'NR==2{print $3}')
DISK_TOTAL=$(df -h / | awk 'NR==2{print $2}')
DISK_PERCENT=$(df -h / | awk 'NR==2{print $5}')
echo "Disk: $DISK_USED / $DISK_TOTAL ($DISK_PERCENT used)"

# Uptime
echo "Uptime: $(uptime -p 2>/dev/null || uptime)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Quick speed test offer
if ping -c 1 -W 2 8.8.8.8 &> /dev/null; then
    echo "Run a quick speed test now? (requires speedtest-cli)"
    read -p "This will take 30-60 seconds [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v speedtest-cli &> /dev/null || python3 -c "import speedtest" 2>/dev/null; then
            echo ""
            echo "Running speed test..."
            python3 -c "
import speedtest
st = speedtest.Speedtest()
st.get_best_server()
download = st.download() / 1_000_000
upload = st.upload() / 1_000_000
ping = st.results.ping
print(f'\nResults:')
print(f'  Download: {download:.2f} Mbps')
print(f'  Upload: {upload:.2f} Mbps')
print(f'  Ping: {ping:.2f} ms')
if download < 800:
    print(f'\n⚠ Speed is below 800 Mbps threshold')
else:
    print(f'\n✓ Speed is above 800 Mbps threshold')
" 2>/dev/null || echo "Error running speed test"
        else
            echo "speedtest-cli not installed"
            echo "Install with: pip3 install speedtest-cli"
        fi
    fi
fi

echo ""
