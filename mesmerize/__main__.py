import argparse
import signal
import threading

from mesmerize.service import MesmerizeService


def main() -> None:
    parser = argparse.ArgumentParser(description="Mesmerize mDNS Firefox control service")
    parser.add_argument("--port", type=int, default=8765, help="HTTP port (default: 8765)")
    parser.add_argument("--name", default="Mesmerize", help="mDNS service name (default: Mesmerize)")
    parser.add_argument("--firefox", default="firefox", help="Firefox executable (default: firefox)")
    args = parser.parse_args()

    service = MesmerizeService(port=args.port, name=args.name, firefox_executable=args.firefox)
    service.start()

    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda s, f: stop.set())

    print("Press Ctrl+C to stop.")
    stop.wait()
    print("\nShutting down...")
    service.stop()


if __name__ == "__main__":
    main()
