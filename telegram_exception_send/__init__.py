import os
import sys
import time
import traceback
import telegram_send

def escape(text: str) -> str:
    """
    Replaces the following chars in `text` ('&' with '&amp;', '<' with '&lt;' and '>' with '&gt;').

    :param text: the text to escape
    :return: the escaped text
    """
    chars = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}
    if text is None:
        return None
    for old, new in chars.items():
        text = text.replace(old, new)
    return text

def _get_caller_script():
    # see if we are in interactive kernel
    try:
        from IPython import get_ipython
        if 'IPKernelApp' in get_ipython().config:  # Jupyter notebook or qtconsole
            return f'Interactive Session, pwd={os.getcwd()}'
    except (ImportError, AttributeError):
        pass
    
    # no caller script
    if sys.argv[0] =='':
        return f'Unknown Script, pwd={os.getcwd()}'
    
    return os.path.abspath(sys.argv[0])


def forward_exception_to_telegram(type, value, tb):
    caller_script =  _get_caller_script()
    trace = ''.join(traceback.format_exception(type, value=value, tb=tb))
    msg = f'{type.__name__} in {caller_script}: {value}\n```\n{trace}\n```'
    telegram_send.send(messages = [escape(msg)])
    # now raise the exception to the original function
    
    try:
        if log_file and isinstance(log_file, str):
            with open(log_file, 'a') as f:
                f.writelines([f'[{time.strftime("%Y.%m.%d-%H:%M:%S")}]: ' + msg])
    finally:
        original_excepthook(type, value, traceback)
    
if telegram_send.utils.get_config_path() in (None, ''):
    raise Exception('Need to configure telegram_send. Please run `telegram-send --configure` in the terminal')

log_file = False

original_excepthook = sys.excepthook
sys.excepthook = forward_exception_to_telegram

