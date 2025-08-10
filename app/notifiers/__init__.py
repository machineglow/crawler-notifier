from . import telegram, email

def send_notification(name, message, config):
    if name == "telegram":
        telegram.send_telegram(message, config)
    elif name == "email":
        email.send_email(message, config)
    else:
        raise ValueError(f"Unknown notifier: {name}")
