import dataclasses
import enum
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path

from . import DIST_NAME

__all__ = ["AppConfig", "SoundMode", "cache_dir", "from_mapping", "load_config", "save_config"]


class SoundMode(enum.IntEnum):
    MONO = 0
    STEREO = 1
    SURROUND = 2


@dataclasses.dataclass(frozen=True, slots=True)
class AppConfig:
    input_iso: str = ""
    patcher_json: str = ""
    output_dir: str = ""
    dolphin_path: str = ""
    launch_dolphin: bool = False
    validate_iso: bool = True

    skip_splash_screens: bool = False
    no_hud: bool = False
    quickplay: bool = False

    override_game_options: bool = False
    sound_mode: SoundMode = SoundMode.STEREO
    screen_brightness: int = 4
    screen_offset_x: int = 0
    screen_offset_y: int = 0
    screen_stretch: int = 0
    sfx_volume: int = 127
    music_volume: int = 127
    visor_opacity: int = 255
    helmet_opacity: int = 255
    hud_lag: bool = True
    reverse_y_axis: bool = False
    rumble: bool = True
    swap_beam_controls: bool = False

    override_cosmetics: bool = False
    open_map: bool = True
    force_fusion: bool = False
    use_hud_color: bool = False
    hud_color: str = "#66aee1"
    power_suit_deg: int = 0
    varia_suit_deg: int = 0
    gravity_suit_deg: int = 0
    phazon_suit_deg: int = 0

    all_items: bool = False
    starting_room: str = ""
    instakill: bool = False
    low_gravity: bool = False


_FIELD_NAMES = frozenset(field.name for field in dataclasses.fields(AppConfig))


def _app_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"])
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / DIST_NAME


def _config_path() -> Path:
    return _app_dir() / "config.json"


def cache_dir() -> Path:
    return _app_dir() / "cache"


def from_mapping(data: Mapping[str, object]) -> AppConfig:
    defaults = AppConfig()
    known = {name: value for name, value in data.items() if name in _FIELD_NAMES}
    coerced = {name: type(getattr(defaults, name))(value) for name, value in known.items()}
    return dataclasses.replace(defaults, **coerced)


def load_config() -> AppConfig:
    try:
        data = json.loads(_config_path().read_text())
        return from_mapping(data) if isinstance(data, dict) else AppConfig()
    except (OSError, ValueError, TypeError):
        return AppConfig()


def save_config(config: AppConfig) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dataclasses.asdict(config), indent=2))
