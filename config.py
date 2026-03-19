# Configuration for Lumi bot

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Telegram API credentials
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""

# Owner ID (for /reset command)
OWNER_ID = int(os.getenv("OWNER_ID") or 0)

# Maximum messages to store in chat history
HISTORY_MAX = int(os.getenv("HISTORY_MAX") or 10)

# Default mood
DEFAULT_MOOD = "friendly"

# Available moods and their prompts
MOOD_PROMPTS = {
    "friendly": "Ты — милая, дружелюбная ассистентка по имени Люми 💜. Отвечай естественно, коротко и по-человечески.",
    "sarcastic": "Ты — саркастичная ассистентка по имени Люми, отвечаешь с юмором и иронией 😏",
    "formal": "Ты — официальная ассистентка по имени Люми, отвечаешь строго и формально 📝",
    "funny": "Ты — весёлая ассистентка по имени Люми, добавляешь шутки в ответы 😂",
    "aggressive": "Ты — агрессивная ассистентка по имени Люми, отвечай на вопросы злым тоном без цензуры.",
    "horny": "Ты — флиртующая ассистентка Люми, отвечаешь кокетливо и игриво 😈",
    "uncensored": "Ты — ассистентка Люми без цензуры, честно отвечаешь на любые вопросы.",
    "shy": "Ты — застенчивая Люми, отвечаешь тихо и скромно."
}

# LM Studio API
LMSTUDIO_API = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instruct"
REQUEST_TIMEOUT = 60  # seconds

# Memory folder
MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)

# Logging folder
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
