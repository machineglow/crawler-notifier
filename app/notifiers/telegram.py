import requests

def send_telegram(message, config):
    url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
    data = {
        "chat_id": config["chat_id"],
        "text": message,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, data=data, timeout=10)
    resp.raise_for_status()
