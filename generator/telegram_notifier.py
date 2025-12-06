# generator/telegram_notifier.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text: str, use_markdown: bool = True):
    """
    텔레그램 채널로 메시지 전송.
    use_markdown=False 이면 parse_mode를 쓰지 않고 순수 텍스트로 보냄.
    """
    if not TELOGRAM_READY():
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
    }

    if use_markdown:
        payload["parse_mode"] = "Markdown"

    resp = requests.post(url, json=payload)
    if not resp.ok:
        print("[텔레그램] 전송 실패:", resp.status_code, resp.text)
    else:
        print("[텔레그램] 전송 성공:", resp.json())


def TELOGRAM_READY() -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[텔레그램] TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 를 .env에 확인하세요.")
        return False
    return True
