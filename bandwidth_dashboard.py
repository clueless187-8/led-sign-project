#!/usr/bin/env python3
"""
Bandwidth Dashboard - Web interface for viewing speed test data
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

DB_PATH = "bandwidth_data.db"
THRESHOLD_MBPS = 800


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/current')
def get_current():
    """Get most recent speed test"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM speed_tests
        ORDER BY timestamp DESC
        LIMIT 1
    ''')

    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({
            'timestamp': result['timestamp'],
            'download_mbps': result['download_mbps'],
            'upload_mbps': result['upload_mbps'],
            'ping_ms': result['ping_ms'],
            'server_location': result['server_location'],
            'isp': result['isp'],
            'below_threshold': bool(result['below_threshold'])
        })
    else:
        return jsonify({'error': 'No data available'}), 404


@app.route('/api/history')
def get_history():
    """Get historical speed test data"""
    hours = request.args.get('hours', default=24, type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM speed_tests
        WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ORDER BY timestamp ASC
    ''', (hours,))

    results = cursor.fetchall()
    conn.close()

    data = []
    for row in results:
        data.append({
            'timestamp': row['timestamp'],
            'download_mbps': row['download_mbps'],
            'upload_mbps': row['upload_mbps'],
            'ping_ms': row['ping_ms'],
            'below_threshold': bool(row['below_threshold'])
        })

    return jsonify(data)


@app.route('/api/stats')
def get_stats():
    """Get statistics for various time periods"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    # Stats for different time periods
    for period_hours, period_name in [(1, '1h'), (24, '24h'), (168, '7d'), (720, '30d')]:
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
        ''', (period_hours,))

        result = cursor.fetchone()

        if result and result['total_tests'] > 0:
            stats[period_name] = {
                'total_tests': result['total_tests'],
                'avg_download': round(result['avg_download'], 2),
                'min_download': round(result['min_download'], 2),
                'max_download': round(result['max_download'], 2),
                'avg_upload': round(result['avg_upload'], 2),
                'avg_ping': round(result['avg_ping'], 2),
                'alerts_count': result['alerts_count']
            }

    conn.close()
    return jsonify(stats)


@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    limit = request.args.get('limit', default=50, type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM speed_tests
        WHERE below_threshold = 1
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))

    results = cursor.fetchall()
    conn.close()

    alerts = []
    for row in results:
        alerts.append({
            'timestamp': row['timestamp'],
            'download_mbps': row['download_mbps'],
            'upload_mbps': row['upload_mbps'],
            'ping_ms': row['ping_ms'],
            'server_location': row['server_location']
        })

    return jsonify(alerts)


@app.route('/api/hourly_average')
def get_hourly_average():
    """Get hourly average speeds for the last 24 hours"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
            AVG(download_mbps) as avg_download,
            AVG(upload_mbps) as avg_upload,
            AVG(ping_ms) as avg_ping,
            MIN(download_mbps) as min_download,
            MAX(download_mbps) as max_download
        FROM speed_tests
        WHERE timestamp >= datetime('now', '-24 hours')
        GROUP BY hour
        ORDER BY hour ASC
    ''')

    results = cursor.fetchall()
    conn.close()

    data = []
    for row in results:
        data.append({
            'hour': row['hour'],
            'avg_download': round(row['avg_download'], 2),
            'avg_upload': round(row['avg_upload'], 2),
            'avg_ping': round(row['avg_ping'], 2),
            'min_download': round(row['min_download'], 2),
            'max_download': round(row['max_download'], 2)
        })

    return jsonify(data)


if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Warning: Database {DB_PATH} not found. Please run bandwidth_monitor.py first.")

    print("Starting Bandwidth Dashboard on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
