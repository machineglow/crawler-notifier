import requests

def send_pushover(message, config):
    """
    Send a notification via Pushover.
    Args:
        message (str): The message to send.
        config (dict): Must contain 'user_key' and 'api_token'.
    """
    user_key = config.get("user_key")
    api_token = config.get("api_token")
    if not user_key or not api_token:
        raise ValueError("Missing Pushover 'user_key' or 'api_token' in config.")

    payload = {
        "token": api_token,
        "user": user_key,
        "message": message
    }
    resp = requests.post("https://api.pushover.net/1/messages.json", data=payload)
    resp.raise_for_status()
