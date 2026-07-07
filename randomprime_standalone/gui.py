import contextlib
import dataclasses
import threading
import tkinter as tk
import traceback
from collections.abc import Callable
from importlib import metadata
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import py_randomprime

from . import dialogs
from .config import AppConfig, from_mapping, load_config, save_config
from .patcher import KNOWN_ISO_SHA1S, build_patch_config, launch_dolphin, output_iso_path, sha1_of

__all__ = ["App"]

_ABOUT = (
    "Applies a randomprime patcher JSON to a vanilla Metroid Prime ISO."
)
_PAD = {"padx": 4, "pady": 4}


def _version_suffix() -> str:
    try:
        return " v" + metadata.version("randomprime-standalone")
    except metadata.PackageNotFoundError:
        return ""


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.patching = False
        self.variables = self._create_variables(load_config())

        root.title("Randomprime Standalone" + _version_suffix())
        root.resizable(False, False)
        self._set_window_icon()
        self._build_ui()

        for variable in self.variables.values():
            variable.trace_add("write", lambda *_: self._on_change())
        self._on_change()

    def _set_window_icon(self) -> None:
        icon = Path(__file__).parent / "assets" / "icon.png"
        with contextlib.suppress(Exception):
            self._icon_image = tk.PhotoImage(file=str(icon))
            self.root.iconphoto(True, self._icon_image)

    def _create_variables(self, config: AppConfig) -> dict[str, tk.Variable]:
        variables: dict[str, tk.Variable] = {}
        for field in dataclasses.fields(AppConfig):
            value = getattr(config, field.name)
            if isinstance(value, bool):
                variables[field.name] = tk.BooleanVar(self.root, value=value)
            elif isinstance(value, int):
                variables[field.name] = tk.IntVar(self.root, value=int(value))
            else:
                variables[field.name] = tk.StringVar(self.root, value=value)
        return variables

    def _snapshot(self) -> AppConfig:
        return from_mapping({name: variable.get() for name, variable in self.variables.items()})

    def _on_change(self) -> None:
        try:
            config = self._snapshot()
        except tk.TclError:
            return
        save_config(config)
        self._refresh_patch_button(config)

    def _refresh_patch_button(self, config: AppConfig) -> None:
        required = [config.input_iso, config.patcher_json, config.output_dir]
        ready = all(required) and not self.patching
        self.patch_button.configure(state="normal" if ready else "disabled")

    def _build_ui(self) -> None:
        body = ttk.Frame(self.root, padding=10)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text=_ABOUT, justify="left").pack(anchor="w", pady=(0, 8))

        files = ttk.LabelFrame(body, text="Files", padding=8)
        files.pack(fill="x")
        files.grid_columnconfigure(1, weight=1)
        rows = (
            ("Patcher JSON", "patcher_json", self._browse_patcher_json),
            ("Input ISO", "input_iso", self._browse_input_iso),
            ("Output Folder", "output_dir", self._browse_output_dir),
            ("Dolphin (optional)", "dolphin_path", self._browse_dolphin),
        )
        for row, (label, name, browse) in enumerate(rows):
            ttk.Label(files, text=label).grid(row=row, column=0, sticky="w", **_PAD)
            ttk.Entry(files, textvariable=self.variables[name], width=60).grid(
                row=row, column=1, sticky="ew", **_PAD
            )
            ttk.Button(files, text="Browse...", command=browse).grid(row=row, column=2, **_PAD)

        preferences = ttk.LabelFrame(body, text="Preferences", padding=8)
        preferences.pack(fill="x", pady=8)
        checks = (
            ("Skip splash screens", "skip_splash_screens"),
            ("Skip main menu", "quickplay"),
            ("Dolphin quickplay after patching", "launch_dolphin"),
            ("Validate input ISO", "validate_iso"),
        )
        for index, (label, name) in enumerate(checks):
            ttk.Checkbutton(preferences, text=label, variable=self.variables[name]).grid(
                row=index // 2, column=index % 2, sticky="w", **_PAD
            )

        dialog_buttons = ttk.Frame(preferences)
        dialog_buttons.grid(row=2, column=0, columnspan=2, sticky="w")
        openers: tuple[tuple[str, Callable[[], None]], ...] = (
            ("Game Options", lambda: dialogs.open_game_options(self.root, self.variables)),
            ("Cosmetics", lambda: dialogs.open_cosmetics(self.root, self.variables)),
            ("Cheats", lambda: dialogs.open_cheats(self.root, self.variables)),
        )
        for label, command in openers:
            ttk.Button(dialog_buttons, text=label, command=command).pack(side="left", **_PAD)

        self.patch_button = ttk.Button(body, text="Patch", command=self._start_patch)
        self.patch_button.pack(fill="x", pady=(4, 4), ipady=4)
        self.progress = ttk.Progressbar(body, maximum=1.0)
        self.progress.pack(fill="x")
        self.status = ttk.Label(body, text="")
        self.status.pack(anchor="w", pady=(4, 0))

    def _browse_input_iso(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Metroid Prime ISO",
            filetypes=[("GameCube ISO", "*.iso *.gcm"), ("All files", "*.*")],
        )
        if path:
            self.variables["input_iso"].set(path)

    def _browse_patcher_json(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Patcher JSON",
            filetypes=[("JSON files", "*.json *.jsonc"), ("All files", "*.*")],
        )
        if path:
            self.variables["patcher_json"].set(path)

    def _browse_output_dir(self) -> None:
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.variables["output_dir"].set(path)

    def _browse_dolphin(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Dolphin Executable",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if path:
            self.variables["dolphin_path"].set(path)

    def _post_progress(self, fraction: float, message: str) -> None:
        self.root.after(0, self._set_progress, fraction, message)

    def _set_progress(self, fraction: float, message: str) -> None:
        self.progress.configure(value=fraction)
        self.status.configure(text=message)

    def _start_patch(self) -> None:
        config = self._snapshot()
        if config.launch_dolphin and not Path(config.dolphin_path).is_file():
            messagebox.showerror(
                "Dolphin Not Found",
                f"Dolphin executable not found at:\n\n{config.dolphin_path or '(no path set)'}",
            )
            return
        self.patching = True
        self._refresh_patch_button(config)
        if not config.validate_iso:
            self._start_patch_worker(config)
            return
        self._set_progress(0.0, "Verifying input ISO...")
        threading.Thread(target=self._checksum_worker, args=(config,), daemon=True).start()

    def _checksum_worker(self, config: AppConfig) -> None:
        try:
            digest = sha1_of(
                Path(config.input_iso),
                lambda fraction: self._post_progress(fraction, "Verifying input ISO..."),
            )
        except OSError:
            self.root.after(0, self._finish, traceback.format_exc(), "")
            return
        self.root.after(0, self._on_checksum_done, config, digest)

    def _on_checksum_done(self, config: AppConfig, digest: str) -> None:
        if digest not in KNOWN_ISO_SHA1S:
            proceed = messagebox.askokcancel(
                "Unknown ISO",
                "The input ISO does not match any known Metroid Prime dump:\n\n"
                f"sha1: {digest}\n\nPatch it anyway?",
            )
            if not proceed:
                self._set_progress(0.0, "Canceled.")
                self._finish(None, "Canceled.")
                return
        self._start_patch_worker(config)

    def _start_patch_worker(self, config: AppConfig) -> None:
        self._set_progress(0.0, "Patching...")
        threading.Thread(target=self._patch_worker, args=(config,), daemon=True).start()

    def _patch_worker(self, config: AppConfig) -> None:
        output_iso = None
        try:
            patch_config = build_patch_config(Path(config.patcher_json), config)
            output_iso = output_iso_path(config.output_dir, patch_config)
            output_iso.parent.mkdir(parents=True, exist_ok=True)
            notifier = py_randomprime.ProgressNotifier(self._post_progress)
            py_randomprime.patch_iso(Path(config.input_iso), output_iso, patch_config, notifier)
        except Exception:
            if output_iso is not None:
                with contextlib.suppress(OSError):
                    output_iso.unlink(missing_ok=True)
            self.root.after(0, self._finish, traceback.format_exc(), "")
            return
        self.root.after(0, self._on_patch_done, config, output_iso)

    def _on_patch_done(self, config: AppConfig, output_iso: Path) -> None:
        if config.launch_dolphin:
            try:
                launch_dolphin(config.dolphin_path, output_iso)
            except OSError:
                self._finish(traceback.format_exc(), "")
                return
        self._finish(None, f"Wrote {output_iso}")

    def _finish(self, error: str | None, message: str) -> None:
        self.patching = False
        self._on_change()
        if error:
            self._set_progress(0.0, "Patching failed.")
            dialogs.show_error(self.root, "Patching Failed", error)
            return
        self.status.configure(text=message)
