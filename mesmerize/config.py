import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    port: int = 8765
    name: str = "Mesmerize"
    firefox_executable: str = "firefox"
    enable_playerctl: bool = True
    enable_observer: bool = True

    @staticmethod
    def load(path: str) -> "Config":
        data = json.loads(Path(path).read_text())
        valid = Config.__dataclass_fields__.keys()
        unknown = data.keys() - valid
        if unknown:
            raise ValueError(f"Unknown config keys: {', '.join(sorted(unknown))}")
        return Config(**{k: v for k, v in data.items() if k in valid})
