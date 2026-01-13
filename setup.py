"""
setup.py for `skjerns-utils`.

• Installs the core package in editable/develop mode
• Presents an optional Tk-GUI that can
    1. copy `startup_imports.py` into IPython’s startup folder
    2. copy `spyder.ini` into the active Spyder profile
    3. install a list of optional dependencies
    4. continue without changes (auto-closes after timeout)

All action buttons disable themselves once clicked; the global countdown
stops on first interaction. Console output is mirrored into the GUI.
"""

from __future__ import annotations

from setuptools import setup

import os
import shutil
import subprocess
import sys
from pathlib import Path
from collections import deque
import traceback

# -----------------------------------------------------------------------------#
# Core metadata + mandatory requirements
# -----------------------------------------------------------------------------#
with open('requirements.txt') as f:
    packages = f.read().splitlines()

if sys.platform.startswith("linux"):
    packages += ["jax"]

setup(
    name="skjerns-utils",
    version="1.20",
    description="A collection of tools and boiler-plate functions",
    url="http://github.com/skjerns/skjerns-utils",
    author="skjerns",
    author_email="nomail",
    license="GNU 2.0",
    install_requires = packages,
    packages=["stimer", "ospath", "cpu_usage", "telegram_send_exception"],
    zip_safe=False,
)



# -----------------------------------------------------------------------------#
# Redirect stdout/stderr to Tk.Text widget
# -----------------------------------------------------------------------------#
class Redirector:
    def __init__(self, text_widget, root):
        self.text = text_widget
        self.root = root
        self._orig_out, self._orig_err = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = self

    def write(self, *args, **kwargs):
        self.text.insert("end", " ".join(args))
        self.text.see("end")
        try:
            self._orig_out.write(*args, **kwargs)
        except UnicodeEncodeError:
            pass
        self.root.update_idletasks()
        self.root.update()

    def flush(self, *args, **kwargs):  # needed for Python >= 3.7
        self._orig_out.flush()
        self._orig_err.flush()

    def restore(self):
        sys.stdout, sys.stderr = self._orig_out, self._orig_err


# -----------------------------------------------------------------------------#
# Tk-inter GUI
# -----------------------------------------------------------------------------#

class InstallPackagesGUI:
    """Optional configuration dialog for skjerns-utils."""

    def __init__(self):
        import tkinter as tk
        from tkinter import Text

        # ───────── configuration ────────────────────────────────────────────
        self.timeout  = 15           # auto-close in s

        # ───────── root window ──────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("Optional configuration")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.root.eval("tk::PlaceWindow . center")

        # ───────── top section (action buttons) ─────────────────────────────
        top = tk.Frame(self.root, bg="black")
        top.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self.btn_spyder = tk.Button(
            top, text="Copy spyder.ini", command=self._copy_spyder
        )
        self.btn_startup = tk.Button(
            top, text="Copy startup_imports.py", command=self._copy_startup
        )
        self.lbl_timeout = tk.Label(
            top, text=f"Closes in {self.timeout}s", bg="black", fg="white"
        )

        self.btn_spyder.pack(side="left", padx=5)
        self.btn_startup.pack(side="left", padx=5)
        self.lbl_timeout.pack(side="right", padx=5)


        # ───────── console (middle) ─────────────────────────────────────────
        self.text_box = Text(
            self.root, wrap="word", height=10, width=110,
            bg="black", fg="white", font=("Consolas", 10)
        )
        self.text_box.grid(row=1, column=0, padx=6, pady=(0,6), sticky="nsew")
        self.redirect = Redirector(self.text_box, self.root)


        # optional explanatory blurb
        print(
            "Select the desired optional actions.\nIf you're unsure what to do, just close this window.\n"
            "Otherwise, the dialog closes automatically.\n"
        )

        # ───────── event wiring / countdown ─────────────────────────────────
        self.root.after(1000, self._countdown)
        self.root.protocol("WM_DELETE_WINDOW", self._destroy)
        self.root.mainloop()


    def _countdown(self):
        if self.timeout == 0:
            self._destroy()
            return
        self.timeout -= 1
        self.lbl_timeout.config(text=f"Closes in {self.timeout}s")
        self.root.after(1000, self._countdown)

    # ---------------------------------------------------------------- actions
    def _copy_startup(self):
        try:
            dst = Path.home() / ".ipython" / "profile_default" / "startup"
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy("startup_imports.py", dst)
            print(f"✓ Copied startup_imports.py → {dst}\n")
            self.btn_startup.config(state="disabled")
        except Exception as e:
            print(f"✗ Error copying startup_imports.py: {e}\n")


    def _copy_spyder(self):
        try:
            import spyder  # noqa: F401
            conf_dir = Path(spyder.config.base.get_conf_path())
        except ModuleNotFoundError:
            home = Path.home()
            conf_dir = next((p for p in
                             (home / ".spyder-py3", home / ".config" / "spyder-py3")
                             if p.exists()), None)
            if conf_dir is None:
                print("✗ No Spyder configuration directory found.\n")
                return
        try:
            dst = conf_dir / "config" / "spyder.ini"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy("spyder.ini", dst)
            print(f"✓ Copied spyder.ini → {dst}\n")
            self.btn_spyder.config(state="disabled")
        except Exception as e:
            print(f"✗ Error copying spyder.ini: {e}\n")

    # ---------------------------------------------------------------- shutdown
    def _destroy(self):
        self.redirect.restore()
        self.root.destroy()


# -----------------------------------------------------------------------------#
# Entry-point
# -----------------------------------------------------------------------------#
if __name__ == "__main__":
    # Running via `pip install -e .` passes arguments; skip GUI when building metadata
    if len(sys.argv) == 1 or sys.argv[1] != "egg_info":
        try:
            InstallPackagesGUI()
        except Exception as exc:  # headless build / missing Tk etc:
            print(f"GUI creation failed – continuing without optional setup. ({exc})")
            print(traceback.format_exc())
