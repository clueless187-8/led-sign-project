# LED Sign Project

A Flask server that drives a 96×16 RGB LED matrix sign from a Raspberry Pi Zero 2W.
It renders six animated effects at 30 FPS and exposes a small HTTP API for
effects, scrolling text, brightness and clearing.

All code lives in [`led-sign-project/`](led-sign-project/) — see its
[README](led-sign-project/README.md) for the effect list and hardware notes.

## Layout

| Path | What it is |
|------|------------|
| `led-sign-project/app.py` | Flask server and HTTP API (port 5000) |
| `led-sign-project/led_driver.py` | Serial driver with USB auto-detection, plus a mock driver |
| `led-sign-project/graphics/ppp_engine.py` | Pixel framebuffer and drawing primitives |
| `led-sign-project/graphics/ppp_animator.py` | Effect loop: rainbow, fire, matrix, stars, pulse, scanner |

## Quick start

```bash
cd led-sign-project
pip3 install -r requirements.txt
python3 app.py
```

The server starts in **mock mode** (`USE_MOCK = True` in `app.py`), so it runs
without hardware. Set `USE_MOCK = False` to drive a real panel; the driver looks
for the first USB/serial port and talks to it at 115200 baud.

## API

| Method | Endpoint | Body | Purpose |
|--------|----------|------|---------|
| GET | `/health` | — | Liveness check |
| GET | `/api/ppp/effects` | — | List available effects |
| GET | `/api/ppp/status` | — | Running effect, FPS, mock mode |
| POST | `/api/ppp/effect` | `{"effect": "fire", "speed": 1.0}` | Start an effect |
| POST | `/api/ppp/stop` | — | Stop the current effect |
| POST | `/api/text` | `{"text": "Hello"}` | Show text |
| POST | `/api/brightness` | `{"level": 7}` | Set brightness |
| POST | `/api/clear` | — | Stop and blank the display |

Example:

```bash
curl -X POST http://<pi-ip>:5000/api/ppp/effect \
     -H 'Content-Type: application/json' -d '{"effect":"matrix"}'
```

## Hardware

- Raspberry Pi Zero 2W
- 96×16 RGB LED matrix panel on USB serial
- 5 V power supply sized for the panel

## Status

Early prototype. The mobile control app mentioned in the inner README is not in
this repository yet.
