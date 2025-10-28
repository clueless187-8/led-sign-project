#!/usr/bin/env python3
"""
Bandwidth Monitor - Track Xfinity internet speeds and detect throttling
Alerts when speed drops below threshold (default: 800 Mbps)
"""

import speedtest
import sqlite3
import time
import json
from datetime import datetime
from pathlib import Path
import logging
import sys

# Configuration
SPEED_THRESHOLD_MBPS = 800  # Alert if speed drops below this
TEST_INTERVAL_SECONDS = 300  # 5 minutes between tests
DB_PATH = "bandwidth_data.db"
LOG_PATH = "bandwidth_monitor.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BandwidthMonitor:
    def __init__(self, db_path=DB_PATH, threshold_mbps=SPEED_THRESHOLD_MBPS):
        self.db_path = db_path
        self.threshold_mbps = threshold_mbps
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with speed test results table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speed_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                download_mbps REAL NOT NULL,
                upload_mbps REAL NOT NULL,
                ping_ms REAL NOT NULL,
                server_host TEXT,
                server_location TEXT,
                isp TEXT,
                below_threshold INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def run_speed_test(self):
        """Execute a speed test and return results"""
        logger.info("Starting speed test...")

        try:
            st = speedtest.Speedtest()
            st.get_best_server()

            # Run download test
            download_bps = st.download()
            download_mbps = download_bps / 1_000_000

            # Run upload test
            upload_bps = st.upload()
            upload_mbps = upload_bps / 1_000_000

            # Get ping
            ping_ms = st.results.ping

            # Get server info
            server_info = st.results.server
            server_host = server_info.get('host', 'Unknown')
            server_location = f"{server_info.get('name', 'Unknown')}, {server_info.get('country', 'Unknown')}"

            # Get ISP
            isp = st.results.client.get('isp', 'Unknown')

            results = {
                'timestamp': datetime.now().isoformat(),
                'download_mbps': round(download_mbps, 2),
                'upload_mbps': round(upload_mbps, 2),
                'ping_ms': round(ping_ms, 2),
                'server_host': server_host,
                'server_location': server_location,
                'isp': isp
            }

            logger.info(f"Speed test complete: ↓{results['download_mbps']} Mbps ↑{results['upload_mbps']} Mbps (ping: {results['ping_ms']}ms)")

            return results

        except Exception as e:
            logger.error(f"Speed test failed: {str(e)}")
            return None

    def save_result(self, results):
        """Save speed test results to database"""
        if not results:
            return

        below_threshold = 1 if results['download_mbps'] < self.threshold_mbps else 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO speed_tests
            (timestamp, download_mbps, upload_mbps, ping_ms, server_host,
             server_location, isp, below_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            results['timestamp'],
            results['download_mbps'],
            results['upload_mbps'],
            results['ping_ms'],
            results['server_host'],
            results['server_location'],
            results['isp'],
            below_threshold
        ))

        conn.commit()
        conn.close()

        logger.info(f"Results saved to database (ID: {cursor.lastrowid})")

        return below_threshold

    def check_and_alert(self, results):
        """Check if speed is below threshold and generate alert"""
        if not results:
            return

        download_speed = results['download_mbps']

        if download_speed < self.threshold_mbps:
            alert_msg = (
                f"⚠️  SPEED ALERT! ⚠️\n"
                f"Download speed: {download_speed} Mbps (below {self.threshold_mbps} Mbps threshold)\n"
                f"Upload speed: {results['upload_mbps']} Mbps\n"
                f"Ping: {results['ping_ms']} ms\n"
                f"Time: {results['timestamp']}\n"
                f"ISP: {results['isp']}"
            )
            logger.warning(alert_msg)

            # Write to alerts file
            with open("bandwidth_alerts.txt", "a") as f:
                f.write(f"\n{'='*60}\n")
                f.write(alert_msg)
                f.write(f"\n{'='*60}\n")

            return True
        else:
            logger.info(f"✓ Speed is above threshold ({download_speed} Mbps >= {self.threshold_mbps} Mbps)")
            return False

    def get_recent_stats(self, hours=24):
        """Get statistics for recent tests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_tests,
                AVG(download_mbps) as avg_download,
                MIN(download_mbps) as min_download,
                MAX(download_mbps) as max_download,
                AVG(upload_mbps) as avg_upload,
                AVG(ping_ms) as avg_ping,
                SUM(below_threshold) as alerts_count
            FROM speed_tests
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ''', (hours,))

        stats = cursor.fetchone()
        conn.close()

        if stats and stats[0] > 0:
            return {
                'total_tests': stats[0],
                'avg_download_mbps': round(stats[1], 2),
                'min_download_mbps': round(stats[2], 2),
                'max_download_mbps': round(stats[3], 2),
                'avg_upload_mbps': round(stats[4], 2),
                'avg_ping_ms': round(stats[5], 2),
                'alerts_count': stats[6]
            }
        return None

    def run_continuous(self, interval=TEST_INTERVAL_SECONDS):
        """Run speed tests continuously at specified interval"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s, threshold: {self.threshold_mbps} Mbps)")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                results = self.run_speed_test()

                if results:
                    self.save_result(results)
                    self.check_and_alert(results)

                    # Show recent stats
                    stats = self.get_recent_stats(24)
                    if stats:
                        logger.info(f"24h stats: Avg={stats['avg_download_mbps']} Mbps, "
                                  f"Min={stats['min_download_mbps']} Mbps, "
                                  f"Max={stats['max_download_mbps']} Mbps, "
                                  f"Alerts={stats['alerts_count']}")

                logger.info(f"Next test in {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Bandwidth Monitor - Track internet speeds')
    parser.add_argument('--threshold', type=int, default=SPEED_THRESHOLD_MBPS,
                       help=f'Speed threshold in Mbps (default: {SPEED_THRESHOLD_MBPS})')
    parser.add_argument('--interval', type=int, default=TEST_INTERVAL_SECONDS,
                       help=f'Test interval in seconds (default: {TEST_INTERVAL_SECONDS})')
    parser.add_argument('--once', action='store_true',
                       help='Run a single test and exit')
    parser.add_argument('--stats', type=int, metavar='HOURS',
                       help='Show statistics for the last N hours and exit')

    args = parser.parse_args()

    monitor = BandwidthMonitor(threshold_mbps=args.threshold)

    if args.stats:
        stats = monitor.get_recent_stats(args.stats)
        if stats:
            print(f"\nStatistics for last {args.stats} hours:")
            print(f"  Total tests: {stats['total_tests']}")
            print(f"  Average download: {stats['avg_download_mbps']} Mbps")
            print(f"  Min download: {stats['min_download_mbps']} Mbps")
            print(f"  Max download: {stats['max_download_mbps']} Mbps")
            print(f"  Average upload: {stats['avg_upload_mbps']} Mbps")
            print(f"  Average ping: {stats['avg_ping_ms']} ms")
            print(f"  Alerts triggered: {stats['alerts_count']}")
        else:
            print(f"No data found for last {args.stats} hours")
    elif args.once:
        results = monitor.run_speed_test()
        if results:
            monitor.save_result(results)
            monitor.check_and_alert(results)
    else:
        monitor.run_continuous(interval=args.interval)


if __name__ == '__main__':
    main()
