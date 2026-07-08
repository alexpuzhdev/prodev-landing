import os
from pathlib import Path

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_CHAT_ID = int(os.environ.get("OWNER_CHAT_ID", "0") or "0")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://app:8000").rstrip("/")
SERVICE_TOKEN = os.environ.get("SERVICE_TOKEN", "")
SITE_URL = os.environ.get("SITE_URL", "https://atrice.ru")
CACHE_TTL = 120
# Прокси до Telegram для локальной разработки за корпоративным egress; на проде пусто
TG_PROXY = os.environ.get("TG_PROXY", "")

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
