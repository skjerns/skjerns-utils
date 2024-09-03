## Exception-Send

Import this library and any uncaught exception will be forwarded via the `telegram-send` command to your telegram bot.

Prerequesit: You have to install and setup `telegram-send` on you machine. Verify in your command line that `telegram-send test` works.

## Usage

```Python
import telegram_send_exception_forward
```

Now, any uncaught exception will result in a telegram message to your bot

```python
3/0 # raises ZeroDivisionError
```

In the background, the exception overwrites the `sys.excepthook` with its own functionality.
