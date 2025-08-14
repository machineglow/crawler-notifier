# notifiers.py

from . import telegram, email, pushbullet, pushover

NOTIFIER_SEND_FUNCTIONS = {
    "telegram": telegram.send_telegram,
    "email": email.send_email,
    "pushbullet": pushbullet.send_pushbullet,
    "pushover": pushover.send_pushover,
}

def send_notification(name, message, config):
    """
    Dispatches a notification to the specified service.

    Args:
        name (str): The name of the notification service (e.g., 'telegram', 'email', 'pushbullet', 'pushover').
        message (str): The message to be sent.
        config (dict): The configuration for the specified notifier.
    """
    try:
        send_func = NOTIFIER_SEND_FUNCTIONS[name]
    except KeyError:
        raise ValueError(f"Unknown notifier: {name}")
    send_func(message, config)