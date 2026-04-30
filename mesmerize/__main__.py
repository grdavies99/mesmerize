import argparse
import signal
import threading

from mesmerize.config import Config
from mesmerize.service import MesmerizeService


def main() -> None:
    parser = argparse.ArgumentParser(description="Mesmerize mDNS Firefox control service")
    parser.add_argument("--config", help="Path to JSON config file")
    args = parser.parse_args()

    cfg = Config.load(args.config) if args.config else Config()

    service = MesmerizeService(
        port=cfg.port,
        name=cfg.name,
        firefox_executable=cfg.firefox_executable,
        enable_playerctl=cfg.enable_playerctl,
        enable_observer=cfg.enable_observer,
    )
    service.start()

    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda s, f: stop.set())

    print("Press Ctrl+C to stop.")
    stop.wait()
    print("\nShutting down...")
    service.stop()


if __name__ == "__main__":
    main()
