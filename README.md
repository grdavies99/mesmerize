# Mesmerize

mDNS-advertised HTTP service for controlling Firefox and media playback on a local machine.

## Requirements

- Python 3.11+
- Firefox installed on the host machine
- `playerctl` for media controls: `sudo apt install playerctl`

## Setup

Clone the repo and set up a virtual environment:

```bash
git clone <repo-url>
cd mesmerize
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The service must run on the machine where Firefox is installed — not over SSH — so that it can open browser windows and control media on the local display.

## Running

```bash
.venv/bin/python -m mesmerize
```

Optional flags:

```
--port     HTTP port (default: 8765)
--name     mDNS service name (default: Mesmerize)
--firefox  Firefox executable path (default: firefox)
```

## Commands

Replace `192.168.1.156` with the IP of the machine running the service.

### Health check

```
curl -s http://192.168.1.156:8765/health
```

### Firefox

```
curl -s -X POST http://192.168.1.156:8765/firefox -H "Content-Type: application/json" -d "{\"args\": [\"--new-tab\", \"https://www.google.com\"]}"
curl -s -X POST http://192.168.1.156:8765/firefox -H "Content-Type: application/json" -d "{\"args\": [\"--new-window\", \"https://www.google.com\"]}"
curl -s -X POST http://192.168.1.156:8765/firefox -H "Content-Type: application/json" -d "{\"args\": [\"--private-window\", \"https://www.google.com\"]}"
curl -s -X POST http://192.168.1.156:8765/firefox -H "Content-Type: application/json" -d "{\"args\": [\"--kiosk\", \"https://www.google.com\"]}"
```

### Media controls

Requires `playerctl`: `sudo apt install playerctl`

```
curl -s -X POST http://192.168.1.156:8765/media -H "Content-Type: application/json" -d "{\"action\": \"play-pause\"}"
curl -s -X POST http://192.168.1.156:8765/media -H "Content-Type: application/json" -d "{\"action\": \"play\"}"
curl -s -X POST http://192.168.1.156:8765/media -H "Content-Type: application/json" -d "{\"action\": \"pause\"}"
curl -s -X POST http://192.168.1.156:8765/media -H "Content-Type: application/json" -d "{\"action\": \"next\"}"
curl -s -X POST http://192.168.1.156:8765/media -H "Content-Type: application/json" -d "{\"action\": \"previous\"}"
curl -s -X POST http://192.168.1.156:8765/media -H "Content-Type: application/json" -d "{\"action\": \"stop\"}"
```
