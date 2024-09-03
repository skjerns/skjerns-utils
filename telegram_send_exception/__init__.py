import os
import sys
import time
import traceback
from html import escape
# bugfix monkeypatch
import telegram
telegram.constants.MAX_MESSAGE_LENGTH = 4096
import telegram_send
import threading


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


# Define the function to send the message
def send_to_telegram_in_thread(msg):
    telegram_send.send(messages=[msg], parse_mode='html')
    print('Forwarded exception via telegram-send')

    # Start the thread for sending the message

# import pysnooper
# @pysnooper.snoop()

def forward_exception_to_telegram(type, value, tb):

    # don't do anything for KeyboardInterrupt and SystemExit
    if not isinstance(value, Exception):
        original_excepthook(type, value, traceback)
        return

    caller_script =  _get_caller_script()
    trace = ''.join(traceback.format_exception(type, value=value, tb=tb))
    msg = f'{type.__name__} in <code>{caller_script}</code>:\n{escape(str(value))}\n<code>\n{escape(trace)}\n</code>'

    telegram_thread = threading.Thread(target=send_to_telegram_in_thread, kwargs={'msg':msg})
    telegram_thread.start()

    # now raise the exception to the original function
    # and write to log if requested
    try:
        if log_file and isinstance(log_file, str):
            with open(log_file, 'a') as f:
                f.writelines([f'[{time.strftime("%Y.%m.%d-%H:%M:%S")}]: ' + msg])
    finally:
        original_excepthook(type, value, traceback)
        # telegram_thread.join()

if telegram_send.utils.get_config_path() in (None, ''):
    raise Exception('Need to configure telegram_send. Please run `telegram-send --configure` in the terminal')

log_file = False

original_excepthook = sys.excepthook
sys.excepthook = forward_exception_to_telegram

if __name__=='__main__':
    raise Exception('TEST!@?@#<>![test]</br>')
