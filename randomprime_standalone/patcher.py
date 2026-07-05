import hashlib
import json
import subprocess
from collections.abc import Callable
from pathlib import Path

from .config import AppConfig, cache_dir

__all__ = ["KNOWN_ISO_SHA1S", "build_patch_config", "launch_dolphin", "output_iso_path", "sha1_of"]

KNOWN_ISO_SHA1S = frozenset({
    "ac20c744db18fdf0339f37945e880708fd317231",  # NTSC 0-00
    "4ba8933499e0b74b2f6006d622e4fbc7593ab3c7",  # NTSC 0-01
    "1a737910b55b59c6ad91be9e3e3c43517fd52efb",  # NTSC 0-02
    "34ac8a764a3c1db3326c39071cee2fc49e730aca",  # PAL
    "ee6c58b46012ebffb615506ec43e02ba71905662",  # Japan
    "15926341f62a24ab3f3f897c0cf767795d2251fd",  # Korean (Source: redump.org)
    "7e1e8d11c9ee50dcb4d71ae020e73b810a67d356",  # NTSC 0-00 + Prime Practice Mod v1.2.5
})

_ALL_ITEMS = {
    "combatVisor": True,
    "powerBeam": True,
    "scanVisor": True,
    "missiles": 250,
    "energyTanks": 14,
    "powerBombs": 8,
    "wave": True,
    "ice": True,
    "plasma": True,
    "charge": True,
    "morphBall": True,
    "bombs": True,
    "spiderBall": True,
    "boostBall": True,
    "powerSuit": 0,
    "variaSuit": True,
    "gravitySuit": True,
    "phazonSuit": True,
    "thermalVisor": True,
    "xray": True,
    "spaceJump": True,
    "grapple": True,
    "superMissile": True,
    "wavebuster": True,
    "iceSpreader": True,
    "flamethrower": True,
    "unknownItem1": 0,
    "unlimitedMissiles": False,
    "unlimitedPowerBombs": False,
    "missileLauncher": True,
    "powerBombLauncher": True,
    "springBall": False,
}


def _hex_to_unit_rgb(color: str) -> list[float]:
    return [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]


def sha1_of(path: Path, on_progress: Callable[[float], None]) -> str:
    digest = hashlib.sha1()
    total = path.stat().st_size
    done = 0
    with path.open("rb") as file:
        while chunk := file.read(4 * 1024 * 1024):
            digest.update(chunk)
            done += len(chunk)
            on_progress(done / total)
    return digest.hexdigest()


def output_iso_path(config: AppConfig) -> Path:
    return Path(config.output_dir) / (Path(config.patcher_json).stem + ".iso")


def _default_game_options(app: AppConfig) -> dict:
    return {
        "soundMode": int(app.sound_mode),
        "screenBrightness": app.screen_brightness,
        "screenOffsetX": app.screen_offset_x,
        "screenOffsetY": app.screen_offset_y,
        "screenStretch": app.screen_stretch,
        "sfxVolume": app.sfx_volume,
        "musicVolume": app.music_volume,
        "visorOpacity": app.visor_opacity,
        "helmetOpacity": app.helmet_opacity,
        "hudLag": app.hud_lag,
        "reverseYAxis": app.reverse_y_axis,
        "rumble": app.rumble,
        "swapBeamControls": app.swap_beam_controls,
    }


def _apply_cosmetics(preferences: dict, tweaks: dict, app: AppConfig) -> None:
    suit_degrees = {
        "powerDeg": app.power_suit_deg,
        "variaDeg": app.varia_suit_deg,
        "gravityDeg": app.gravity_suit_deg,
        "phazonDeg": app.phazon_suit_deg,
    }
    preferences["noHud"] = app.no_hud
    preferences["mapDefaultState"] = "Always" if app.open_map else "MapStationOrVisit"
    preferences["forceFusion"] = app.force_fusion
    preferences["suitColors"] = {name: degrees for name, degrees in suit_degrees.items() if degrees}
    if app.use_hud_color:
        tweaks["hudColor"] = _hex_to_unit_rgb(app.hud_color)


def build_patch_config(patcher_json: Path, app: AppConfig) -> dict:
    config = json.loads(patcher_json.read_text())

    cache = cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    preferences = {
        "skipSplashScreens": app.skip_splash_screens,
        "cacheDir": str(cache),
    }
    config.setdefault("preferences", {}).update(preferences)
    if app.override_game_options:
        config["preferences"]["defaultGameOptions"] = _default_game_options(app)

    tweaks = config.setdefault("tweaks", {})
    if app.instakill:
        tweaks["gunDamage"] = 100.0
    if app.low_gravity:
        tweaks["gravity"] = 0.33
    if app.override_cosmetics:
        _apply_cosmetics(config["preferences"], tweaks, app)

    game_config = config.setdefault("gameConfig", {})
    if app.all_items:
        game_config["startingItems"] = dict(_ALL_ITEMS)
    if app.starting_room:
        game_config["startingRoom"] = app.starting_room

    return config


def launch_dolphin(dolphin_path: str, iso: Path) -> None:
    dolphin = Path(dolphin_path)
    subprocess.Popen([str(dolphin), "-b", "-e", str(iso)], cwd=dolphin.parent)
