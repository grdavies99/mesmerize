import json
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from zeroconf import ServiceInfo, Zeroconf

SERVICE_TYPE = "_mesmerize._tcp.local."

_MEDIA_ACTIONS = {"play", "pause", "play-pause", "next", "previous", "stop"}


class _FirefoxHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok"})
        else:
            self._respond(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/media":
            self._handle_media()
            return


        if self.path != "/firefox":
            self._respond(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
            args = data.get("args", [])
            if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
                raise ValueError("args must be a list of strings")
        except (json.JSONDecodeError, ValueError) as exc:
            self._respond(400, {"error": str(exc)})
            return

        firefox = self.server.firefox_executable
        try:
            proc = subprocess.Popen(
                [firefox, *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._respond(200, {"pid": proc.pid, "status": "launched"})
        except FileNotFoundError:
            self._respond(500, {"error": f"Firefox not found at '{firefox}'"})

    def _handle_media(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
            action = data.get("action", "")
            if action not in _MEDIA_ACTIONS:
                raise ValueError(f"action must be one of: {', '.join(sorted(_MEDIA_ACTIONS))}")
        except (json.JSONDecodeError, ValueError) as exc:
            self._respond(400, {"error": str(exc)})
            return

        try:
            subprocess.run(["playerctl", action], check=True, capture_output=True)
            self._respond(200, {"action": action, "status": "ok"})
        except FileNotFoundError:
            self._respond(500, {"error": "playerctl not found — install with: apt install playerctl"})
        except subprocess.CalledProcessError as exc:
            self._respond(500, {"error": exc.stderr.decode().strip() or "playerctl failed"})

    def _respond(self, code: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):  # silence default access log
        pass


class _MesmerizeHTTPServer(HTTPServer):
    def __init__(self, port: int, firefox_executable: str):
        super().__init__(("", port), _FirefoxHandler)
        self.firefox_executable = firefox_executable


class MesmerizeService:
    """mDNS-advertised HTTP service for executing Firefox CLI commands."""

    def __init__(
        self,
        port: int = 8765,
        name: str = "Mesmerize",
        firefox_executable: str = "firefox",
    ):
        self.port = port
        self.name = name
        self.firefox_executable = firefox_executable
        self._zeroconf: Zeroconf | None = None
        self._server: _MesmerizeHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        local_ip = _local_ip()

        self._server = _MesmerizeHTTPServer(self.port, self.firefox_executable)

        self._zeroconf = Zeroconf()
        info = ServiceInfo(
            SERVICE_TYPE,
            f"{self.name}.{SERVICE_TYPE}",
            addresses=[socket.inet_aton(local_ip)],
            port=self.port,
            properties={"version": "1.0"},
        )
        self._zeroconf.register_service(info)

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        print(f"Mesmerize listening on http://{local_ip}:{self.port}")
        print(f"mDNS service: {self.name}.{SERVICE_TYPE}")

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server = None
        if self._zeroconf:
            self._zeroconf.unregister_all_services()
            self._zeroconf.close()
            self._zeroconf = None


def _local_ip() -> str:
    """Return the machine's primary LAN IP (not 127.0.0.1)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"
