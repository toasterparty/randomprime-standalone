import contextlib
import ctypes
import sys
import tkinter as tk
import traceback
from tkinter import messagebox

from randomprime_standalone.gui import App


def main() -> None:
    if sys.platform == "win32":
        with contextlib.suppress(OSError):
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    try:
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception:
        messagebox.showerror("Fatal Error", traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
