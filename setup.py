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
packages_full = ['absl-py',
                 'alog',
                 'autoreject',
                 'beautifulsoup4',
                 'bleak',
                 'clipboard',
                 'certstore',
                 'coverage',
                 'dateparser',
                 'dominate',
                 'h5io',
                 'imageio',
                 'joblib',
                 'lspopt',
                 'lz4',
                 'mat73',
                 'mne',
                 'mne-bids-pipeline',
                 'monitorcontrol',
                 'natsort',
                 'networkx',
                 'numba',
                 'numpy',
                 'numpyencoder',
                 'opencv-python',
                 'pandas',
                 'pingouin',
                 'pip-system-certs',
                 'prettytable',
                 'pybids',
                 'pybind11',
                 'pyedflib',
                 'pyexcel',
                 'pyexcel-ods',
                 'pyexcel-ods3',
                 'pygame',
                 'pyglet',
                 'pymupdf',
                 'pytablewriter',
                 'python-picard',
                 'python-pptx',
                 'requests',
                 'scikit-learn',
                 'scipy',
                 'seaborn',
                 'sleep_utils',
                 'standard-imghdr',
                 'statsmodels',
                 'spyder-kernels',
                 'telegram-send',
                 'truststore',
                 'tqdm',
                 'wmi']

if sys.platform.startswith("linux"):
    packages_full += ["jax"]

setup(
    name="skjerns-utils",
    version="1.20",
    description="A collection of tools and boiler-plate functions",
    url="http://github.com/skjerns/skjerns-utils",
    author="skjerns",
    author_email="nomail",
    license="GNU 2.0",
    install_requires=["tqdm", "natsort", "telegram-send"],
    extras_require={"full": packages_full},
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
        from tkinter import ttk, Text

        # ───────── configuration ────────────────────────────────────────────
        self.timeout  = 15           # auto-close in s
        self.counting = True         # stop when a cb is toggled

        # ───────── root window ──────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("Optional configuration")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.root.eval("tk::PlaceWindow . center")

        # ───────── top section (check-boxes + action button) ────────────────
        top = tk.Frame(self.root, bg="black")
        top.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # --- check-boxes (all start unchecked) -----------------------------
        self.var_spyder   = tk.BooleanVar(master=self.root, value=False)
        self.var_startup  = tk.BooleanVar(master=self.root, value=False)

        self.chk_spyder  = tk.Checkbutton(
            top, text="install spyder.ini",
            variable=self.var_spyder, command=self._on_select,
            bg="black", fg="white", anchor="w", selectcolor="black",
        )
        self.chk_startup = tk.Checkbutton(
            top, text="install ipython startup_imports.py",
            variable=self.var_startup, command=self._on_select,
            bg="black", fg="white", anchor="w", selectcolor="black",
        )

        self.chk_spyder.pack(fill="x", anchor="w")
        self.chk_startup.pack(fill="x", anchor="w")

        # --- action button --------------------------------------------------
        self.btn_action = tk.Button(
            top, text=f"Close ({self.timeout})", width=14,
            fg="green", command=self._on_action
        )
        self.btn_action.pack(side="right", padx=12, pady=2)

        # ───────── console (middle) ─────────────────────────────────────────
        self.text_box = Text(
            self.root, wrap="word", height=10, width=110,
            bg="black", fg="white", font=("Consolas", 10)
        )
        self.text_box.grid(row=1, column=0, padx=6, pady=(0,6), sticky="nsew")
        self.redirect = Redirector(self.text_box, self.root)


        # optional explanatory blurb
        print(
            "Select the desired optional actions (checkboxes).\nIf you're unsure what to do, just click close.\n"
            "Otherwise, the dialog closes automatically.\n"
        )

        # ───────── event wiring / countdown ─────────────────────────────────
        self.root.after(1000, self._countdown)
        self.root.protocol("WM_DELETE_WINDOW", self._destroy)
        self.root.mainloop()

    # ------------------------------------------------------------------ helpers
    def _on_select(self, *_):
        """User toggled at least one checkbox → stop timer, change button."""
        if self.counting:
            self.counting = False
            self.btn_action.config(text="Install", fg="red")

    def _start_close_timer(self, secs: int = 15) -> None:
        self._close_timeout = secs
        self._tick_close_timer()

    def _tick_close_timer(self) -> None:
        if self._close_timeout <= 0:
            self._destroy()
            return
        self.btn_action.config(text=f"Close ({self._close_timeout})")
        self._close_timeout -= 1
        self.root.after(1000, self._tick_close_timer)

    def _on_action(self):
        """Run selected tasks once, then turn the button into a real ‘Close’."""

        # If we are already in “close” mode → just close
        if getattr(self, "_actions_done", False):
            self._destroy()
            return

        if self.counting:          # timer expired without interaction
            self._destroy()
            return

        # disable further changes
        self.chk_spyder.config(state="disabled")
        self.chk_startup.config(state="disabled")
        self.btn_action.config(state="disabled")

        # perform selected tasks
        if self.var_spyder.get():
            self._copy_spyder()
        if self.var_startup.get():
            self._copy_startup()

        # ➌ finished: convert button to a *true* close-button
        self._actions_done = True               # flag: tasks already executed
        self.btn_action.config(
            text="Close (15)",
            fg="green",
            state="normal",
            command=self._destroy,               # single-click → close
        )

        # ➍ kick off post-install auto-close
        self._start_close_timer(secs=15)
    # ---------------------------------------------------------------- countdown
    def _countdown(self):
        if not self.counting:
            return
        if self.timeout == 0:
            self._destroy()
            return
        self.timeout -= 1
        self.btn_action.config(text=f"Close ({self.timeout})")
        self.root.after(1000, self._countdown)

    # ---------------------------------------------------------------- actions
    def _copy_startup(self):
        dst = Path.home() / ".ipython" / "profile_default" / "startup"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy("startup_imports.py", dst)
        print(f"✓ Copied startup_imports.py → {dst}\n")

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
        dst = conf_dir / "config" / "spyder.ini"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy("spyder.ini", dst)
        print(f"✓ Copied spyder.ini → {dst}\n")

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
