import requests

def send_telegram_message(token, chat_id, message):
    """Sends a message via the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown" # Allows for bold/italic text
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)