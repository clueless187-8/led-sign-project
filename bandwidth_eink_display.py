#!/usr/bin/env python3
"""
E-Ink Display for Bandwidth Monitor
Shows current speed, statistics, and alerts on e-ink display
Supports multiple Waveshare e-paper HAT sizes
"""

import os
import sys
import time
import sqlite3
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import logging

# Configuration
DB_PATH = "bandwidth_data.db"
UPDATE_INTERVAL = 300  # 5 minutes (matches speed test interval)
THRESHOLD_MBPS = 800

# E-Ink Display Configuration
# Supported displays: '2.13', '2.9', '4.2', '7.5'
DISPLAY_SIZE = os.getenv('EINK_DISPLAY_SIZE', '2.13')

# Font paths (try multiple locations)
FONT_PATHS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_font(size=12):
    """Find available font on system"""
    for font_path in FONT_PATHS:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
    # Fallback to default font
    return ImageFont.load_default()


class EInkDisplay:
    """Base class for e-ink display"""

    def __init__(self, size='2.13'):
        self.size = size
        self.epd = None
        self.width = 0
        self.height = 0

        # Display dimensions
        self.display_configs = {
            '2.13': {'width': 250, 'height': 122, 'module': 'epd2in13_V3'},
            '2.9': {'width': 296, 'height': 128, 'module': 'epd2in9_V2'},
            '4.2': {'width': 400, 'height': 300, 'module': 'epd4in2'},
            '7.5': {'width': 800, 'height': 480, 'module': 'epd7in5_V2'},
        }

        if size not in self.display_configs:
            logger.error(f"Unsupported display size: {size}")
            logger.info(f"Supported sizes: {', '.join(self.display_configs.keys())}")
            sys.exit(1)

        config = self.display_configs[size]
        self.width = config['width']
        self.height = config['height']
        self.module_name = config['module']

        # Try to import the e-ink driver
        try:
            # Add waveshare library path
            libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
            if os.path.exists(libdir):
                sys.path.append(libdir)

            # Try importing waveshare module
            module = __import__(f'waveshare_epd.{self.module_name}', fromlist=[self.module_name])
            EPD = getattr(module, 'EPD')
            self.epd = EPD()
            logger.info(f"Initialized {size}\" e-ink display ({self.width}x{self.height})")
        except ImportError as e:
            logger.error(f"Failed to import e-ink driver: {e}")
            logger.info("Running in simulation mode (no display hardware)")
            self.epd = None

    def init(self):
        """Initialize the display"""
        if self.epd:
            try:
                self.epd.init()
                self.epd.Clear()
                logger.info("Display initialized and cleared")
            except Exception as e:
                logger.error(f"Failed to initialize display: {e}")

    def display_image(self, image):
        """Display image on e-ink screen"""
        if self.epd:
            try:
                self.epd.display(self.epd.getbuffer(image))
                logger.info("Image displayed on e-ink")
            except Exception as e:
                logger.error(f"Failed to display image: {e}")
        else:
            # Simulation mode - save to file
            image.save('eink_simulation.png')
            logger.info("Simulation mode: saved to eink_simulation.png")

    def sleep(self):
        """Put display to sleep"""
        if self.epd:
            try:
                self.epd.sleep()
            except Exception as e:
                logger.error(f"Failed to sleep display: {e}")


def get_db_connection():
    """Create database connection"""
    if not os.path.exists(DB_PATH):
        logger.error(f"Database not found: {DB_PATH}")
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_latest_speed():
    """Get most recent speed test result"""
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM speed_tests
        ORDER BY timestamp DESC
        LIMIT 1
    ''')

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'timestamp': result['timestamp'],
            'download_mbps': result['download_mbps'],
            'upload_mbps': result['upload_mbps'],
            'ping_ms': result['ping_ms'],
            'below_threshold': bool(result['below_threshold'])
        }
    return None


def get_statistics(hours=24):
    """Get statistics for time period"""
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            COUNT(*) as total_tests,
            AVG(download_mbps) as avg_download,
            MIN(download_mbps) as min_download,
            MAX(download_mbps) as max_download,
            SUM(below_threshold) as alerts_count
        FROM speed_tests
        WHERE timestamp >= datetime('now', '-' || ? || ' hours')
    ''', (hours,))

    result = cursor.fetchone()
    conn.close()

    if result and result['total_tests'] > 0:
        return {
            'total_tests': result['total_tests'],
            'avg_download': round(result['avg_download'], 1),
            'min_download': round(result['min_download'], 1),
            'max_download': round(result['max_download'], 1),
            'alerts_count': result['alerts_count']
        }
    return None


def create_display_image(display, current, stats):
    """Create image for e-ink display"""

    # Create blank white image
    image = Image.new('1', (display.width, display.height), 255)
    draw = ImageDraw.Draw(image)

    # Determine font sizes based on display size
    if display.width >= 400:  # Large displays (4.2", 7.5")
        title_font = find_font(32)
        speed_font = find_font(56)
        label_font = find_font(20)
        stats_font = find_font(18)
        small_font = find_font(14)
    elif display.width >= 250:  # Medium displays (2.13", 2.9")
        title_font = find_font(16)
        speed_font = find_font(28)
        label_font = find_font(12)
        stats_font = find_font(10)
        small_font = find_font(8)
    else:
        title_font = find_font(12)
        speed_font = find_font(20)
        label_font = find_font(10)
        stats_font = find_font(8)
        small_font = find_font(6)

    y_pos = 5

    # Title
    draw.text((5, y_pos), "XFINITY BANDWIDTH", font=title_font, fill=0)
    y_pos += 25 if display.width >= 400 else 18

    # Current speed data
    if current:
        download = current['download_mbps']
        upload = current['upload_mbps']
        ping = current['ping_ms']
        is_alert = current['below_threshold']

        # Alert indicator
        if is_alert:
            draw.text((5, y_pos), "⚠ BELOW 800 MBPS", font=label_font, fill=0)
            y_pos += 20 if display.width >= 400 else 12

        # Download speed (main focus)
        draw.text((5, y_pos), "↓ Download", font=label_font, fill=0)
        y_pos += 25 if display.width >= 400 else 15

        speed_text = f"{download:.0f}"
        draw.text((10, y_pos), speed_text, font=speed_font, fill=0)

        # Mbps label
        mbps_x = 10 + draw.textlength(speed_text, font=speed_font)
        draw.text((mbps_x + 5, y_pos + 10), "Mbps", font=label_font, fill=0)

        y_pos += 45 if display.width >= 400 else 30

        # Upload and Ping in smaller text
        info_text = f"↑ {upload:.0f} Mbps  •  Ping: {ping:.0f} ms"
        draw.text((5, y_pos), info_text, font=stats_font, fill=0)
        y_pos += 20 if display.width >= 400 else 12

        # Timestamp
        try:
            dt = datetime.fromisoformat(current['timestamp'])
            time_str = dt.strftime('%b %d %I:%M %p')
        except:
            time_str = "Unknown time"

        draw.text((5, y_pos), f"Last test: {time_str}", font=small_font, fill=0)
        y_pos += 18 if display.width >= 400 else 12

    else:
        draw.text((5, y_pos), "No data available", font=label_font, fill=0)
        y_pos += 30

    # Statistics (24h)
    if stats and display.height > 200:  # Only on taller displays
        draw.line([(5, y_pos), (display.width - 5, y_pos)], fill=0, width=1)
        y_pos += 10

        draw.text((5, y_pos), "24 HOUR STATS", font=label_font, fill=0)
        y_pos += 18 if display.width >= 400 else 12

        stats_text = [
            f"Avg: {stats['avg_download']} Mbps",
            f"Min: {stats['min_download']} Mbps",
            f"Max: {stats['max_download']} Mbps",
            f"Tests: {stats['total_tests']}",
        ]

        if stats['alerts_count'] > 0:
            stats_text.append(f"⚠ Alerts: {stats['alerts_count']}")

        for line in stats_text:
            draw.text((5, y_pos), line, font=stats_font, fill=0)
            y_pos += 16 if display.width >= 400 else 10

    # Footer with threshold
    footer_y = display.height - 15 if display.width >= 400 else display.height - 10
    draw.text((5, footer_y), f"Threshold: {THRESHOLD_MBPS} Mbps", font=small_font, fill=0)

    return image


def main():
    """Main loop"""
    logger.info(f"Starting E-Ink Bandwidth Display (Size: {DISPLAY_SIZE}\")")
    logger.info(f"Update interval: {UPDATE_INTERVAL}s, Threshold: {THRESHOLD_MBPS} Mbps")

    # Initialize display
    display = EInkDisplay(DISPLAY_SIZE)
    display.init()

    try:
        while True:
            logger.info("Updating display...")

            # Get current data
            current = get_latest_speed()
            stats = get_statistics(24)

            if current:
                logger.info(f"Current speed: ↓{current['download_mbps']:.1f} Mbps "
                          f"↑{current['upload_mbps']:.1f} Mbps")

            # Create and display image
            image = create_display_image(display, current, stats)
            display.display_image(image)

            logger.info(f"Next update in {UPDATE_INTERVAL} seconds...")
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        display.sleep()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        display.sleep()
        sys.exit(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='E-Ink Bandwidth Display')
    parser.add_argument('--size', type=str, default=DISPLAY_SIZE,
                       choices=['2.13', '2.9', '4.2', '7.5'],
                       help='E-ink display size in inches')
    parser.add_argument('--interval', type=int, default=UPDATE_INTERVAL,
                       help='Update interval in seconds')
    parser.add_argument('--threshold', type=int, default=THRESHOLD_MBPS,
                       help='Speed threshold in Mbps')
    parser.add_argument('--test', action='store_true',
                       help='Generate test image and exit')

    args = parser.parse_args()

    DISPLAY_SIZE = args.size
    UPDATE_INTERVAL = args.interval
    THRESHOLD_MBPS = args.threshold

    if args.test:
        # Test mode - generate single image
        logger.info("Test mode: generating single image")
        display = EInkDisplay(DISPLAY_SIZE)

        # Use real data if available, otherwise fake data
        current = get_latest_speed()
        if not current:
            current = {
                'timestamp': datetime.now().isoformat(),
                'download_mbps': 856.3,
                'upload_mbps': 42.1,
                'ping_ms': 12.4,
                'below_threshold': False
            }

        stats = get_statistics(24)
        if not stats:
            stats = {
                'total_tests': 48,
                'avg_download': 842.5,
                'min_download': 798.2,
                'max_download': 923.1,
                'alerts_count': 2
            }

        image = create_display_image(display, current, stats)
        image.save(f'eink_test_{DISPLAY_SIZE}.png')
        logger.info(f"Test image saved to: eink_test_{DISPLAY_SIZE}.png")
    else:
        main()
