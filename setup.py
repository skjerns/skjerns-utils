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
packages_opt = [
    # heavy numerical / plotting
    ["numpy", "scipy", "scikit-learn", "joblib", "numba", "imageio", "seaborn",
     "h5io", "pingouin", "mat73", "numpyencoder", "networkx", "pandas", "statsmodels"],
    # file-format helpers
    ["pyexcel", "pyexcel-ods", "pyexcel-ods3", "python-pptx"],
    # EEG / M/EEG stack
    ["mne", "python-picard", "autoreject", "sleep_utils", "lspopt", "pybids"],
    ["alog", "absl-py"],
    # misc singletons
    "pyedflib",
    "pytablewriter",
    "pybind11",
    "bleak",
    "coverage",
    "natsort",
    "prettytable",
    "pysnooper",
    "clipboard",
    "dateparser",
    "opencv-python",
    "pygame",
    "dominate",
    "pyglet",
    "beautifulsoup4",
    "wmi",
    "compress-pickle",
    "lz4",
    "monitorcontrol",
    "requests>=2.27.0",
]
if sys.platform.startswith("linux"):
    packages_opt += ["jax"]

setup(
    name="skjerns-utils",
    version="1.17",
    description="A collection of tools and boiler-plate functions",
    url="http://github.com/skjerns/skjerns-utils",
    author="skjerns",
    author_email="nomail",
    license="GNU 2.0",
    install_requires=["tqdm", "natsort", "python-telegram-bot==13.5", "telegram-send==0.34", "requests>=2.27.0"],
    packages=["stimer", "ospath", "cpu_usage", "telegram_send_exception"],
    zip_safe=False,
)

# -----------------------------------------------------------------------------#
# Helper for installing optional packages
# -----------------------------------------------------------------------------#
def _pip_install(pkg, err_tail: int = 20) -> bool:
    """
    Install one or more packages with pip and stream output line-by-line.

    Parameters
    ----------
    pkg : str | Sequence[str]
        Package name or an iterable of package names.
    err_tail : int, default 20
        Number of trailing output lines to repeat if the installation fails.

    Returns
    -------
    bool
        True if ``pip`` exited with return-code 0, otherwise False.

    Notes
    -----
    * ``stderr`` is merged into ``stdout`` to ensure error messages are visible
      in real-time.
    * If the command fails, the last *err_tail* lines are replayed so that the
      user can immediately see the relevant error context above the ☓ banner.
    """
    cmd: list[str] = (
        [sys.executable, "-m", "pip", "install", *pkg]
        if isinstance(pkg, (list, tuple, set))
        else [sys.executable, "-m", "pip", "install", str(pkg)]
    )

    # Ring buffer to keep the most recent lines for later replay if needed
    recent: deque[str] = deque(maxlen=err_tail)

    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,      # merge stderr → stdout
        text=True,                     # decode bytes automatically
        bufsize=1,                     # line-buffered
    ) as proc:
        for line in proc.stdout:       # iterate line-by-line
            print(line, end="", flush=True)
            recent.append(line)

    if proc.returncode != 0:
        banner = f"\n✗ Could not install {pkg!r} (exit code {proc.returncode})"
        print(banner, flush=True)
        if recent:
            print("─────────── last pip messages ───────────", flush=True)
            for line in recent:
                print(line, end="", flush=True)
        return False

    return True

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
    """Optional configuration dialog for skjerns-utils (final layout)."""

    def __init__(self, optional_packages):
        import tkinter as tk
        from tkinter import ttk, Text

        # ───────── configuration ────────────────────────────────────────────
        self.pkgs     = optional_packages
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
        self.var_deps     = tk.BooleanVar(master=self.root, value=False)

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
        self.chk_deps    = tk.Checkbutton(
            top, text="install additional packages",
            variable=self.var_deps, command=self._on_select,
            bg="black", fg="white", anchor="w", selectcolor="black",
        )

        self.chk_spyder.pack(fill="x", anchor="w")
        self.chk_startup.pack(fill="x", anchor="w")
        self.chk_deps.pack(fill="x", anchor="w")

        # --- action button --------------------------------------------------
        self.btn_action = tk.Button(
            top, text=f"Close ({self.timeout})", width=14,
            fg="green", command=self._on_action
        )
        self.btn_action.pack(side="right", padx=12, pady=2)

        # ───────── console (middle) ─────────────────────────────────────────
        self.text_box = Text(
            self.root, wrap="word", height=18, width=110,
            bg="black", fg="white", font=("Consolas", 10)
        )
        self.text_box.grid(row=1, column=0, padx=6, sticky="nsew")
        self.redirect = Redirector(self.text_box, self.root)

        # ───────── progress bar (bottom) ────────────────────────────────────
        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", mode="determinate",
            maximum=len(self.pkgs), length=500
        )
        self.progress.grid(row=2, column=0, padx=6, pady=(4,6), sticky="ew")

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
        self.chk_deps.config(state="disabled")
        self.btn_action.config(state="disabled")

        # perform selected tasks
        if self.var_spyder.get():
            self._copy_spyder()
        if self.var_startup.get():
            self._copy_startup()
        if self.var_deps.get():
            self._install_pkgs()

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

    def _install_pkgs(self):
        if not self.pkgs:
            return
        print("Starting installation of optional dependencies …\n")
        for idx, pkg in enumerate(self.pkgs, start=1):
            self.progress["value"] = idx
            if not _pip_install(pkg):
                break
        print("\n✓ All requested packages processed.\n")

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
            InstallPackagesGUI(packages_opt)
        except Exception as exc:  # headless build / missing Tk etc.
            print(f"GUI creation failed – continuing without optional setup. ({exc})")
            print(traceback.format_exc())
