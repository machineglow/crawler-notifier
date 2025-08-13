import requests
import logging

logger = logging.getLogger(__name__)

def send_pushbullet(message, config):
    """
    Sends a notification via Pushbullet.

    Args:
        message (str): The message content to send.
        config (dict): A dictionary containing the notifier's configuration,
                       including the 'api_key'.
    """
    api_key = config.get("api_key")
    if not api_key:
        logger.error("Pushbullet API key is missing from the configuration.")
        return

    try:
        data = {
            "type": "note",
            "title": "New Deal Alert",
            "body": message
        }
        headers = {
            "Access-Token": api_key,
            "Content-Type": "application/json"
        }
        response = requests.post("https://api.pushbullet.com/v2/pushes", headers=headers, json=data)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
        logger.info("Pushbullet notification sent successfully.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Pushbullet notification: {e}")

