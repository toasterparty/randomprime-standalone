import colorsys
import contextlib
import tkinter as tk
from collections.abc import Mapping
from tkinter import colorchooser, ttk

from .config import SoundMode
from .rooms import STARTING_ROOMS

__all__ = ["open_cheats", "open_cosmetics", "open_game_options", "show_error"]

_UNCHANGED_ROOM = "(unchanged)"

_SOUND_MODE_LABELS = {
    SoundMode.MONO: "Mono",
    SoundMode.STEREO: "Stereo",
    SoundMode.SURROUND: "Dolby Surround",
}

_SUIT_PREVIEW_COLORS = {
    "power": ((255, 173, 50), (200, 40, 45), (120, 210, 70)),
    "varia": ((240, 150, 40), (210, 40, 45), (255, 120, 50), (120, 210, 70)),
    "gravity": ((170, 170, 150), (70, 30, 60), (40, 30, 100), (140, 220, 220)),
    "phazon": ((60, 60, 60), (25, 25, 25), (220, 50, 60)),
}


def _dialog(parent: tk.Misc, title: str) -> ttk.Frame:
    window = tk.Toplevel(parent)
    window.title(title)
    window.transient(parent)
    window.resizable(False, False)
    window.wait_visibility()
    window.grab_set()
    body = ttk.Frame(window, padding=10)
    body.pack(fill="both", expand=True)
    return body


def _close_button(body: ttk.Frame) -> None:
    ttk.Button(body, text="Close", command=body.winfo_toplevel().destroy).pack(pady=(10, 0))


def _group(body: ttk.Frame, title: str) -> ttk.LabelFrame:
    frame = ttk.LabelFrame(body, text=title, padding=8)
    frame.pack(fill="x", pady=(0, 8))
    return frame


def _check(parent: tk.Misc, label: str, variable: tk.Variable) -> None:
    ttk.Checkbutton(parent, text=label, variable=variable).pack(anchor="w")


def _scale(parent: tk.Misc, label: str, variable: tk.Variable, low: int, high: int) -> None:
    row = ttk.Frame(parent)
    row.pack(fill="x")
    ttk.Label(row, text=label, width=18).pack(side="left")
    tk.Scale(
        row, variable=variable, from_=low, to=high, orient="horizontal", length=240
    ).pack(side="left", fill="x", expand=True)


def _rotate_hue(rgb: tuple[int, int, int], degrees: int) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(*(channel / 255 for channel in rgb))
    r, g, b = colorsys.hsv_to_rgb((h + degrees / 360) % 1.0, s, v)
    return round(r * 255), round(g * 255), round(b * 255)


def _to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _set_enabled(widget: tk.Misc, enabled: bool) -> None:
    for child in widget.winfo_children():
        state = "normal" if enabled else "disabled"
        if enabled and isinstance(child, ttk.Combobox):
            state = "readonly"
        with contextlib.suppress(tk.TclError):
            child.configure(state=state)
        _set_enabled(child, enabled)


def _suit_row(
    parent: tk.Misc, label: str, variable: tk.Variable, base_colors: tuple[tuple[int, int, int], ...]
) -> None:
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=2)
    ttk.Label(row, text=label, width=12).pack(side="left")
    squares = [tk.Label(row, width=2, relief="sunken") for _ in base_colors]
    for square in squares:
        square.pack(side="left", padx=1)

    def repaint(value: object) -> None:
        degrees = int(float(value))
        for square, color in zip(squares, base_colors):
            square.configure(background=_to_hex(_rotate_hue(color, degrees)))

    tk.Scale(
        row, variable=variable, from_=0, to=359, orient="horizontal", length=160, command=repaint
    ).pack(side="left", fill="x", expand=True, padx=(8, 0))
    repaint(variable.get())


def open_game_options(parent: tk.Misc, variables: Mapping[str, tk.Variable]) -> None:
    body = _dialog(parent, "Game Options")

    override = variables["override_game_options"]
    options = ttk.Frame(body)

    def refresh_enabled() -> None:
        _set_enabled(options, override.get())

    ttk.Checkbutton(
        body, text="Override game options", variable=override, command=refresh_enabled
    ).pack(anchor="w", pady=(0, 8))
    options.pack(fill="x")

    display = _group(options, "Display")
    _scale(display, "Screen Brightness", variables["screen_brightness"], 0, 8)
    _scale(display, "Screen Offset X", variables["screen_offset_x"], -30, 30)
    _scale(display, "Screen Offset Y", variables["screen_offset_y"], -30, 30)
    _scale(display, "Screen Stretch", variables["screen_stretch"], -10, 10)

    audio = _group(options, "Audio")
    sound_row = ttk.Frame(audio)
    sound_row.pack(fill="x", pady=(0, 4))
    ttk.Label(sound_row, text="Sound Mode", width=18).pack(side="left")
    sound_combo = ttk.Combobox(
        sound_row,
        values=[_SOUND_MODE_LABELS[mode] for mode in SoundMode],
        state="readonly",
        width=16,
    )
    sound_combo.current(int(variables["sound_mode"].get()))
    sound_combo.bind(
        "<<ComboboxSelected>>", lambda _event: variables["sound_mode"].set(sound_combo.current())
    )
    sound_combo.pack(side="left")
    _scale(audio, "Sound FX Volume", variables["sfx_volume"], 0, 127)
    _scale(audio, "Music Volume", variables["music_volume"], 0, 127)

    hud = _group(options, "HUD")
    _scale(hud, "Visor Opacity", variables["visor_opacity"], 0, 255)
    _scale(hud, "Helmet Opacity", variables["helmet_opacity"], 0, 255)
    _check(hud, "HUD Lag", variables["hud_lag"])

    controls = _group(options, "Controls")
    _check(controls, "Invert Y Axis", variables["reverse_y_axis"])
    _check(controls, "Rumble", variables["rumble"])
    _check(controls, "Swap Beam Controls", variables["swap_beam_controls"])

    refresh_enabled()
    _close_button(body)


def open_cosmetics(parent: tk.Misc, variables: Mapping[str, tk.Variable]) -> None:
    body = _dialog(parent, "Cosmetics")

    override = variables["override_cosmetics"]
    options = ttk.Frame(body)

    def refresh_enabled() -> None:
        _set_enabled(options, override.get())

    ttk.Checkbutton(
        body, text="Override cosmetic options", variable=override, command=refresh_enabled
    ).pack(anchor="w", pady=(0, 8))
    options.pack(fill="x")

    general = _group(options, "General")
    _check(general, "No HUD", variables["no_hud"])
    _check(general, "Open map by default", variables["open_map"])
    _check(general, "Force Fusion suit", variables["force_fusion"])

    hud = _group(options, "HUD Color")
    _check(hud, "Use custom HUD color", variables["use_hud_color"])
    color_row = ttk.Frame(hud)
    color_row.pack(fill="x", pady=(4, 0))
    swatch = tk.Label(color_row, width=4, relief="sunken", background=variables["hud_color"].get())
    swatch.pack(side="left")

    def pick_color() -> None:
        (_, hex_color) = colorchooser.askcolor(variables["hud_color"].get(), parent=body)
        if hex_color:
            variables["hud_color"].set(hex_color)
            swatch.configure(background=hex_color)

    ttk.Button(color_row, text="Pick...", command=pick_color).pack(side="left", padx=(8, 0))

    suits = _group(options, "Suit Hue Rotation (degrees)")
    _suit_row(suits, "Power Suit", variables["power_suit_deg"], _SUIT_PREVIEW_COLORS["power"])
    _suit_row(suits, "Varia Suit", variables["varia_suit_deg"], _SUIT_PREVIEW_COLORS["varia"])
    _suit_row(suits, "Gravity Suit", variables["gravity_suit_deg"], _SUIT_PREVIEW_COLORS["gravity"])
    _suit_row(suits, "Phazon Suit", variables["phazon_suit_deg"], _SUIT_PREVIEW_COLORS["phazon"])

    refresh_enabled()
    _close_button(body)


def open_cheats(parent: tk.Misc, variables: Mapping[str, tk.Variable]) -> None:
    body = _dialog(parent, "Cheats")

    cheats = _group(body, "Cheats")
    _check(cheats, "Start with all items", variables["all_items"])
    _check(cheats, "Instakill", variables["instakill"])
    _check(cheats, "Low gravity", variables["low_gravity"])

    room_row = ttk.Frame(cheats)
    room_row.pack(fill="x", pady=(8, 0))
    ttk.Label(room_row, text="Starting Room").pack(side="left", padx=(0, 8))
    room_combo = ttk.Combobox(
        room_row,
        values=(_UNCHANGED_ROOM, *STARTING_ROOMS),
        state="readonly",
        width=44,
        height=25,
    )
    room_combo.set(variables["starting_room"].get() or _UNCHANGED_ROOM)

    def on_room_selected(_event: tk.Event) -> None:
        selected = room_combo.get()
        variables["starting_room"].set("" if selected == _UNCHANGED_ROOM else selected)

    room_combo.bind("<<ComboboxSelected>>", on_room_selected)
    room_combo.pack(side="left", fill="x", expand=True)

    _close_button(body)


def show_error(parent: tk.Misc, title: str, message: str) -> None:
    window = tk.Toplevel(parent)
    window.title(title)
    window.transient(parent)
    window.wait_visibility()
    window.grab_set()
    text = tk.Text(window, width=100, height=25, wrap="word")
    text.insert("1.0", message)
    text.configure(state="disabled")
    scroll = ttk.Scrollbar(window, command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    text.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
    scroll.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)
    ttk.Button(window, text="Close", command=window.destroy).grid(
        row=1, column=0, columnspan=2, pady=(0, 10)
    )
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
