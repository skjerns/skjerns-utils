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

# -----------------------------------------------------------------------------#
# Core metadata + mandatory requirements
# -----------------------------------------------------------------------------#
packages_opt = [
    # heavy numerical / plotting
    ["numpy", "scipy", "scikit-learn", "joblib", "numba", "imageio", "seaborn", "h5io"],
    # file-format helpers
    ["pyexcel", "pyexcel-ods", "pyexcel-ods3", "python-pptx"],
    # EEG / M/EEG stack
    ["mne", "python-picard", "autoreject"],
    # misc singletons
    "demandimport",
    "dill",
    "pyedflib",
    "mat73",
    "lspopt",
    "pytablewriter",
    "pybind11",
    "bleak",
    "coverage",
    "natsort",
    "prettytable",
    "pysnooper",
    "clipboard",
    "telegram-send",
    "dateparser",
    "opencv-python",
    "pygame",
    "dominate",
    "pyglet",
    "beautifulsoup4",
    "wmi",
    "networkx",
    "numpyencoder",
    "compress-pickle",
    "absl-py",
    "lz4",
    "monitorcontrol",
    "alog",
    "sleep_utils",
    "pingouin",
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
    install_requires=["tqdm", "natsort", "python-telegram-bot==13.5", "telegram-send==0.34"],
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
        self._orig_out.write(*args, **kwargs)
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
    def __init__(self, optional_packages):
        import tkinter as tk
        from tkinter import ttk, Text, Button  # local import → no dependency for headless

        # ---------------- state ----------------
        self.pkgs = optional_packages
        self.timeout = 15
        self.counting = True  # stop after first action

        # ---------------- root -----------------
        self.root = tk.Tk()
        self.root.configure(bg="black")
        self.root.eval("tk::PlaceWindow . center")
        self.root.title("Optional configuration")
        self.root.resizable(False, False)

        # ---------------- console --------------
        self.text_box = Text(
            self.root,
            wrap="word",
            height=20,
            width=120,
            bg="black",
            fg="white",
            font=("Consolas", 10),
        )
        self.text_box.grid(column=0, row=0, columnspan=9, sticky="nsew", padx=5, pady=5)
        self.redirect = Redirector(self.text_box, self.root)

        print(
            "You may now\n"
            " 1) copy startup_imports.py to the IPython startup folder\n"
            " 2) copy spyder.ini to your Spyder profile\n"
            " 3) install optional dependencies\n\n"
            "Choose nothing to continue unmodified.\n"
        )

        # ---------------- buttons --------------
        self.btn_startup = Button(
            self.root,
            text="Copy IPython startup script",
            command=self._action_startup,
            width=28,
            height=2,
        )
        self.btn_startup.grid(column=0, row=1, padx=2, pady=6)

        self.btn_spyder = Button(
            self.root,
            text="Copy spyder.ini",
            command=self._action_spyder,
            width=20,
            height=2,
        )
        self.btn_spyder.grid(column=1, row=1, padx=2)

        self.btn_install = Button(
            self.root,
            text="Install optional deps",
            command=self._action_install,
            width=24,
            height=2,
            fg="red",
        )
        self.btn_install.grid(column=2, row=1, padx=2)

        self.btn_continue = Button(
            self.root,
            text=f"Continue ({self.timeout})",
            command=self._destroy,
            width=12,
            height=2,
            fg="green",
        )
        self.btn_continue.grid(column=3, row=1, padx=10)

        # ---------------- progress bar ---------
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            mode="determinate",
            maximum=len(self.pkgs),
            length=320,
        )
        self.progress.grid(column=4, row=1, columnspan=5, padx=10, pady=8)

        # ---------------- wiring ---------------
        self.root.after(1000, self._countdown)
        self.root.protocol("WM_DELETE_WINDOW", self._destroy)
        self.root.mainloop()

    # ---------------------------------------------------------------------
    # Countdown management
    # ---------------------------------------------------------------------
    def _countdown(self):
        if not self.counting:
            return
        if self.timeout == 0:
            self._destroy()
            return
        self.timeout -= 1
        self.btn_continue.config(text=f"Continue ({self.timeout})")
        self.root.after(1000, self._countdown)

    def _stop_countdown(self):
        self.counting = False
        self.btn_continue.config(text="Continue")

    # ---------------------------------------------------------------------
    # Actions
    # ---------------------------------------------------------------------
    def _action_startup(self):
        self._stop_countdown()
        self.btn_startup.config(state="disabled")
        self._copy_startup()

    def _action_spyder(self):
        self._stop_countdown()
        self.btn_spyder.config(state="disabled")
        self._copy_spyder()

    def _action_install(self):
        self._stop_countdown()
        self.btn_install.config(state="disabled")
        self._install_pkgs()

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _copy_startup(self):
        dst = Path.home() / ".ipython" / "profile_default" / "startup"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy("startup_imports.py", dst)
        print(f"✓ Copied startup_imports.py → {dst}\n")

    def _copy_spyder(self):
        try:
            import spyder  # noqa: F401  (import to locate config)
            conf_dir = Path(spyder.config.base.get_conf_path())
        except ModuleNotFoundError:
            home = Path.home()
            for p in (home / ".spyder-py3", home / ".config" / "spyder-py3"):
                conf_dir = p
                if p.exists():
                    break
            else:
                print("✗ No Spyder configuration directory found.\n")
                return
        dst = conf_dir / "config" / "spyder.ini"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy("spyder.ini", dst)
        print(f"✓ Copied spyder.ini → {dst}\n")

    def _install_pkgs(self):
        print("Starting installation of optional dependencies …\n")
        for idx, pkg in enumerate(self.pkgs, start=1):
            self.progress["value"] = idx
            _pip_install(pkg)
        print("\n✓ All requested packages processed.\n")

    # ---------------------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------------------
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
