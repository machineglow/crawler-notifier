from . import telegram, email, pushbullet

def send_notification(name, message, config):
    """
    Dispatches a notification to the specified service.

    Args:
        name (str): The name of the notification service (e.g., 'telegram', 'email', 'pushbullet').
        message (str): The message to be sent.
        config (dict): The configuration for the specified notifier.
    """
    if name == "telegram":
        telegram.send_telegram(message, config)
    elif name == "email":
        email.send_email(message, config)
    elif name == "pushbullet":
        pushbullet.send_pushbullet(message, config)
    else:
        raise ValueError(f"Unknown notifier: {name}")
