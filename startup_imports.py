# system level imports, should never fail
@profile
def main():
    import os
    import sys
    import io
    import importlib
    import inspect
    import shutil
    import tempfile
    import builtins
    import warnings
    import subprocess
    import unittest

    # lazy loading of external modules
    def lazy_import(name):
        try:
            spec = importlib.util.find_spec(name)
            module = importlib.util.module_from_spec(spec)
            loader = importlib.util.LazyLoader(spec.loader)
            spec.loader = loader
            sys.modules[name] = module
            loader.exec_module(module)
            return module

        except AttributeError as e:
            print(f"[startup_imports] Failed to load '{name}': {e}")
        return None

    try:
        np = lazy_import('numpy')
        tqdm = lazy_import('tqdm').tqdm
        mlp = lazy_import('matplotlib')
        pickle = lazy_import('pickle')
        sns = lazy_import('seaborn')
    except Exception as e:
        print(f'[startup_imports] Error while loading module: {e}')

    # Dummy clause. Just for correct linting in file.
    if []==():
        plt, get_ipython = None  # will not actually be executed


    # check if run in console or in script
    def is_in_script():
        try:
            return get_ipython().__class__.__name__=='EZMQInteractiveShell'
        except:
            return True

    #%% this makes debugging unittests line by line much easier
    class _DummyTestClass(unittest.TestCase):
        def __getattribute__(self, item):
            if not (item  in ['__class__', 'runTest','addTypeEqualityFunc', '_type_equality_funcs' ]) \
            and not (item in unittest.TestCase.__dict__):
                if is_in_script():
                    print('this function should not be called within a script, only from command line\n' +
                                      'make sure all calls to cls/self are assigned. Tried read  {}'.format(item))
            return object.__getattribute__(self, item)
        def __setattr__(self, item, value):
            if not (item  in ['__class__', 'runTest','addTypeEqualityFunc', '_type_equality_funcs' ]) \
            and not (item in unittest.TestCase.__dict__) and not (item.startswith('_')):
                if is_in_script():
                    print('this function should not be called within a script, only from command line\n' +
                                      'make sure all calls to cls/self are assigned. Tried set  {}'.format(item))
            return object.__setattr__(self, item, value)

    self = _DummyTestClass()
    cls = self

    #######
    # pass-through wrapper for line-profiler / kernprof

    try: # pass t
        builtins.profile
    except AttributeError:
        # No line profiler, provide a pass-through version
        def profile(func):
            import traceback
            print(f'WARNING: @profile debugger active for {func}()')
            print(traceback.format_stack(limit=2)[0])
            return func
        builtins.profile = profile


    #%% plt maximize figure // DISABLED ###################

    import matplotlib.pyplot as plt

    #### make matplotlib fullscreen on second screen automatically

    # def check_extended_display():
    #     """returns true if two monitors are detected and OS=win. Always false on Linux."""
    #     try:
    #         from win32api import GetSystemMetrics
    #         t_width, t_height = GetSystemMetrics(79), GetSystemMetrics(78)
    #         c_width, c_height = GetSystemMetrics(1), GetSystemMetrics(0)

    #         if t_width==c_width and c_height==t_height:
    #             return False
    #     except ModuleNotFoundError:
    #         return False
    #     return True


    # def _new_figure(num=None, figsize=None, dpi=None, **kwargs):
    #     """
    #     This convenience function creates figures
    #     on the second screen automatically and maximizes
    #     """
    #     if num is not None and num in plt.get_fignums():
    #         return plt._figure(num=num, figsize=figsize, dpi=dpi, **kwargs)

    #     fig = plt._figure(num=num, figsize=figsize, dpi=dpi, **kwargs)

    #     # check if we are actually running a window or are in an inline-plot
    #     is_windowed = hasattr(fig.canvas.manager, 'window')
    #     if not is_windowed: return fig

    #     # move window to second screen
    #     window = fig.canvas.manager.window
    #     if plt.second_monitor and check_extended_display() and hasattr(window, 'move'):
    #         fig.canvas.manager.window.move(2100,400)

    #     # maximizing window
    #     if plt.maximize and figsize is None:
    #         if hasattr(window, 'showMaximized'):
    #             fig.canvas.manager.window.showMaximized()
    #         else:
    #             print(f"[startup_imports.py] Can't maximize figure for window:"
    #                   f"{fig.canvas.manager}.{window}. showMaximized() not found")
    #     return fig

    # def _pause_without_putting_figure_on_top(interval):
    #     figs = plt.get_fignums()

    #     if len(figs)==0:
    #         return plt._pause(interval)

    #     td = interval/len(figs)
    #     for fignum in figs:
    #         fig = plt.figure(fignum)
    #         fig.canvas.draw_idle()
    #         fig.canvas.start_event_loop(td)


    # plt._pause = plt.pause
    # plt.pause = _pause_without_putting_figure_on_top

    # plt._figure = plt.figure
    # plt.figure = _new_figure
    # plt.maximize = True
    # plt.second_monitor = True
    plt.rcParams['svg.fonttype'] = 'none' #w hen saving svg, keep text as text


    #%% MONKEY-PATCH: & Ctrl+C clipboard for figures

    # ---------- clipboard helper ----------
    def _copy_figure_to_clipboard(fig):
        """Send *fig* as bitmap to the system clipboard."""
        import sys
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        data = buf.getvalue()
        buf.close()

        plat = sys.platform
        if plat == "darwin":                                 # macOS
            subprocess.run(["pbcopy"], input=data)
        elif plat.startswith("linux"):                       # Linux/Wayland/X11
            if shutil.which("wl-copy"):
                subprocess.run(["wl-copy", "--type", "image/png"], input=data)
            elif shutil.which("xclip"):
                subprocess.run(
                    ["xclip", "-selection", "clipboard", "-t", "image/png", "-i"],
                    input=data,
                )
            else:
                warnings.warn("No wl-copy/xclip found – can't copy figure")
        elif plat.startswith("win"):                         # Windows
            try:
                import win32clipboard, win32con
                from PIL import Image
                im = Image.open(io.BytesIO(data)).convert("RGB")
                tmp = io.BytesIO()
                im.save(tmp, "BMP")
                bmp = tmp.getvalue()[14:]  # strip 14-byte BMP header
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_DIB, bmp)
                win32clipboard.CloseClipboard()
            except Exception as e:  # pragma: no cover
                warnings.warn(f"Clipboard copy failed: {e}")
        else:
            warnings.warn(f"Unsupported OS for clipboard copy: {plat}")

    # ---------- per-figure injection ----------
    def _inject(fig):
        import sys
        if getattr(fig, "_auto_injected", False):
            return fig

        # Ctrl+C handler
        def _on_key(evt):
            if evt.key and evt.key.lower() in ("ctrl+c", "control+c"):
                _copy_figure_to_clipboard(fig)
                print("[startup_imports] Figure copied to clipboard")

        fig.canvas.mpl_connect("key_press_event", _on_key)
        fig._auto_injected = True
        return fig

    # ---------- wire the injector into every creation path ----------
    _old_new_figure = plt.figure                       # came from earlier patch
    def _patched_new_figure(*a, **k):
        return _inject(_old_new_figure(*a, **k))
    plt.figure = _patched_new_figure                    # override again

    _old_subplots = plt.subplots
    def _patched_subplots(*a, **k):
        fig, ax = _old_subplots(*a, **k)
        return _inject(fig), ax
    plt.subplots = _patched_subplots

    _orig_Figure_init = plt.Figure.__init__
    def _patched_Figure_init(self, *a, **k):
        _orig_Figure_init(self, *a, **k)
        _inject(self)
    plt.Figure.__init__ = _patched_Figure_init

    print("[startup_imports] monkey-patch + Ctrl+C clipboard enabled")


    #%% Change the warnings module such that the source line is not printed
    def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
        return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
    warnings.formatwarning = warning_on_one_line

    np.set_printoptions(suppress=True)

    #%% wurn off numpy scientific notation printing


    # # overwrite print function with pprint
    # def pprint_wrapper(*args, sep=' ', end='\n', file=sys.stdout, flush=False):
    #     """
    #     Wrapper for pretty-print. Forwards to print.
    #     Prints the values to a stream, or to sys.stdout by default.

    #     Optional keyword arguments:
    #     file:  a file-like object (stream); defaults to the current sys.stdout.
    #     sep:   string inserted between values, default a space.
    #     end:   string appended after the last value, default a newline.
    #     flush: whether to forcibly flush the stream.
    #     """
    #     if len(args)==1:
    #         if not isinstance(args[0], str):
    #             args = [pformat(args[0])]
    #     __print(*args, sep=sep, end=end, file=file, flush=flush)
    # __print = print

    # print = pprint_wrapper
    # builtins.print = pprint_wrapper
main()
