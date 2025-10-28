# Bandwidth Monitor for Xfinity Internet

A comprehensive tool to monitor your Xfinity internet speeds, detect throttling, and identify unauthorized bandwidth usage.

## Features

- **Automated Speed Testing**: Continuously monitors download/upload speeds and ping
- **800 Mbps Threshold Alerts**: Automatically alerts when speed drops below 800 Mbps
- **Historical Data**: SQLite database stores all test results with timestamps
- **Web Dashboard**: Beautiful real-time dashboard with charts and statistics
- **Alert Logging**: Separate log file for all speed violations
- **Statistics**: View averages, min/max speeds for various time periods

## Quick Start

### 1. Install Dependencies

```bash
cd led-sign-project
pip install -r requirements.txt
```

### 2. Run Your First Speed Test

```bash
# Single test
python3 bandwidth_monitor.py --once

# View results
cat bandwidth_monitor.log
```

### 3. Start Continuous Monitoring

```bash
# Monitor every 5 minutes (default)
python3 bandwidth_monitor.py

# Custom interval (e.g., every 2 minutes)
python3 bandwidth_monitor.py --interval 120

# Custom threshold (e.g., 900 Mbps)
python3 bandwidth_monitor.py --threshold 900
```

### 4. Launch Web Dashboard

In a separate terminal:

```bash
python3 bandwidth_dashboard.py
```

Then open your browser to: **http://localhost:5001**

## Usage Examples

### Single Speed Test
```bash
python3 bandwidth_monitor.py --once
```

### View Statistics
```bash
# Last 24 hours
python3 bandwidth_monitor.py --stats 24

# Last 7 days
python3 bandwidth_monitor.py --stats 168
```

### Custom Monitoring
```bash
# Test every 10 minutes with 900 Mbps threshold
python3 bandwidth_monitor.py --interval 600 --threshold 900
```

### View Alerts
```bash
# Check alert log
cat bandwidth_alerts.txt

# View detailed logs
tail -f bandwidth_monitor.log
```

## Running as a Background Service

### Option 1: Using systemd (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/bandwidth-monitor.service
```

Add this content:

```ini
[Unit]
Description=Bandwidth Monitor Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/user/led-sign-project
ExecStart=/usr/bin/python3 /home/user/led-sign-project/bandwidth_monitor.py --interval 300 --threshold 800
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bandwidth-monitor.service
sudo systemctl start bandwidth-monitor.service

# Check status
sudo systemctl status bandwidth-monitor.service

# View logs
sudo journalctl -u bandwidth-monitor.service -f
```

### Option 2: Using cron (Periodic Tests)

```bash
# Edit crontab
crontab -e

# Add this line to run every 5 minutes
*/5 * * * * cd /home/user/led-sign-project && /usr/bin/python3 bandwidth_monitor.py --once >> /home/user/led-sign-project/cron.log 2>&1
```

### Option 3: Using screen (Simple Background Process)

```bash
# Start a screen session
screen -S bandwidth

# Run the monitor
python3 bandwidth_monitor.py

# Detach from screen: Press Ctrl+A, then D

# Reattach later
screen -r bandwidth
```

## Dashboard Service

To run the dashboard as a service:

```bash
sudo nano /etc/systemd/system/bandwidth-dashboard.service
```

Add:

```ini
[Unit]
Description=Bandwidth Dashboard Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/user/led-sign-project
ExecStart=/usr/bin/python3 /home/user/led-sign-project/bandwidth_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bandwidth-dashboard.service
sudo systemctl start bandwidth-dashboard.service
```

## Database Information

- **Location**: `bandwidth_data.db`
- **Type**: SQLite
- **Schema**:
  - `id`: Unique test ID
  - `timestamp`: Test time (ISO format)
  - `download_mbps`: Download speed
  - `upload_mbps`: Upload speed
  - `ping_ms`: Ping latency
  - `server_host`: Speed test server
  - `server_location`: Server location
  - `isp`: Internet service provider
  - `below_threshold`: Alert flag (1 if below threshold)

### Query Database Manually

```bash
sqlite3 bandwidth_data.db

# View all tests
SELECT * FROM speed_tests ORDER BY timestamp DESC LIMIT 10;

# View alerts only
SELECT timestamp, download_mbps FROM speed_tests WHERE below_threshold = 1;

# Average speed by hour
SELECT strftime('%Y-%m-%d %H:00', timestamp) as hour,
       AVG(download_mbps) as avg_speed
FROM speed_tests
GROUP BY hour;
```

## Monitoring Recommendations

### For Throttling Detection
- **Interval**: Every 5-10 minutes during peak hours
- **Duration**: Run for at least 24-48 hours
- **Look for**: Patterns of speed drops at specific times (e.g., evenings)

### For Unauthorized Usage Detection
- **Interval**: Every 1-2 minutes during suspected usage
- **Action**: Check connected devices on your router
- **Compare**: Speed tests before and after disconnecting suspicious devices

### Data Collection Tips
1. **Baseline**: Run tests during known idle times to establish normal speeds
2. **Peak Hours**: Increase frequency during evenings (6pm-11pm)
3. **Overnight**: Monitor overnight for unusual activity
4. **Before/After**: Test before calling Xfinity support for documentation

## Web Dashboard Features

- **Real-time Speed Display**: Current download/upload/ping
- **Visual Alerts**: Highlighted boxes when below threshold
- **Historical Charts**: Line graphs showing speed over time
- **Hourly Averages**: Bar chart of average speeds by hour
- **Statistics Panel**: 24h averages, min/max speeds
- **Alert List**: Recent violations with timestamps
- **Auto-refresh**: Updates every 60 seconds

## Troubleshooting

### Speed test fails
```bash
# Test speedtest-cli manually
speedtest-cli --simple

# If that fails, install/reinstall
pip install --upgrade speedtest-cli
```

### Permission errors
```bash
# Make scripts executable
chmod +x bandwidth_monitor.py
chmod +x bandwidth_dashboard.py
```

### Database locked
```bash
# Stop all monitoring processes
pkill -f bandwidth_monitor.py

# Restart
python3 bandwidth_monitor.py
```

### Dashboard shows no data
```bash
# Ensure monitor is running first
python3 bandwidth_monitor.py --once

# Check database exists
ls -lh bandwidth_data.db

# Verify data
sqlite3 bandwidth_data.db "SELECT COUNT(*) FROM speed_tests;"
```

## File Structure

```
led-sign-project/
├── bandwidth_monitor.py       # Main monitoring script
├── bandwidth_dashboard.py     # Web dashboard server
├── templates/
│   └── dashboard.html         # Dashboard UI
├── bandwidth_data.db          # SQLite database (created on first run)
├── bandwidth_monitor.log      # Main log file
├── bandwidth_alerts.txt       # Alert log file
└── requirements.txt           # Python dependencies
```

## Evidence Collection for ISP Issues

If you suspect throttling and need to contact Xfinity:

1. **Collect Data**: Run monitor for 48+ hours
2. **Generate Report**:
   ```bash
   python3 bandwidth_monitor.py --stats 168
   ```
3. **Export Database**: Copy `bandwidth_data.db` for records
4. **Screenshot Dashboard**: Capture charts showing speed drops
5. **Check Alerts**: Review `bandwidth_alerts.txt` for violations

## Tips for Optimal Results

- **Wired Connection**: Use Ethernet for accurate results (not WiFi)
- **No Background Activity**: Close downloads/streaming during tests
- **Router Reboot**: Restart router before starting monitoring
- **Server Selection**: Speedtest automatically selects best server
- **Multiple Locations**: Run from different devices if possible

## Command Line Reference

```bash
# Monitor with defaults (5 min interval, 800 Mbps threshold)
python3 bandwidth_monitor.py

# Single test only
python3 bandwidth_monitor.py --once

# Custom interval (seconds)
python3 bandwidth_monitor.py --interval 60

# Custom threshold (Mbps)
python3 bandwidth_monitor.py --threshold 900

# View statistics for last N hours
python3 bandwidth_monitor.py --stats 24

# Run dashboard
python3 bandwidth_dashboard.py
```

## Support

For issues or questions:
- Check logs: `bandwidth_monitor.log`
- View alerts: `bandwidth_alerts.txt`
- Database queries: `sqlite3 bandwidth_data.db`

## License

This tool is for personal network monitoring only. Use responsibly and in accordance with your ISP's terms of service.
