import subprocess

_ACTIONS = {"play", "pause", "play-pause", "next", "previous", "stop"}


class PlayerctlError(Exception):
    pass


def run_action(action: str) -> None:
    if action not in _ACTIONS:
        raise ValueError(f"action must be one of: {', '.join(sorted(_ACTIONS))}")
    _run(["playerctl", action])


def skip_to(position: float) -> None:
    if position < 0:
        raise ValueError("position must be >= 0")
    _run(["playerctl", "position", str(position)])


def seek_by(offset: float) -> None:
    prefix = "+" if offset >= 0 else ""
    _run(["playerctl", "position", f"{prefix}{offset}"])


def set_volume(level: float) -> None:
    if not 0.0 <= level <= 1.0:
        raise ValueError("volume level must be between 0.0 and 1.0")
    _run(
        ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", str(level)],
        not_found_msg="wpctl not found — install with: apt install wireplumber",
    )


def get_position() -> float:
    return float(_query(["playerctl", "position"]))


def get_volume() -> float:
    # output format: "Volume: 0.75000"
    raw = _query(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
    return float(raw.split()[1])


def _run(cmd: list[str], not_found_msg: str = "playerctl not found — install with: apt install playerctl") -> None:
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except FileNotFoundError:
        raise PlayerctlError(not_found_msg)
    except subprocess.CalledProcessError as exc:
        raise PlayerctlError(exc.stderr.decode().strip() or f"{cmd[0]} failed")


def _query(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, check=True, capture_output=True)
        return result.stdout.decode().strip()
    except FileNotFoundError:
        raise PlayerctlError("playerctl not found — install with: apt install playerctl")
    except subprocess.CalledProcessError as exc:
        raise PlayerctlError(exc.stderr.decode().strip() or f"{cmd[0]} failed")
