# LM Studio API call utilities

import httpx
from config import LMSTUDIO_API, MODEL_NAME, REQUEST_TIMEOUT
from utils.memory import get_notes
from config import MOOD_PROMPTS, DEFAULT_MOOD
from bot import HISTORY, MODEL_MOOD, CHAT_USERS  # circular import may require restructuring

async def ask_model(prompt: str, chat_id: int, sender_id: int) -> str:
    """Send a prompt to LM Studio and return the response."""
    # Get last messages for context
    chat_history = HISTORY.get(chat_id, [])
    last_messages = "\n".join(
        f"{sender}: {msg}" for sender, msg in chat_history[-10:]
    )

    mood = MODEL_MOOD.get(chat_id, DEFAULT_MOOD)
    mood_text = MOOD_PROMPTS.get(mood, "")

    username = CHAT_USERS.get(sender_id, f"user{sender_id}")

    memory_text = "\n".join(get_notes(chat_id)) or "— нет записей —"

    system_content = f"""
Ты — женская ассистентка Люми. Отвечай кратко и по фактам.

{mood_text}

Сейчас к тебе обращается {username}.
История чата (последние 10 сообщений):
{last_messages}

Записанная память:
{memory_text}
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 500
    }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            resp = await client.post(LMSTUDIO_API, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "⚠️ Модель временно недоступна.")
        except httpx.HTTPStatusError:
            return "⚠️ Люми не видит локальную модель. Запусти LM Studio."
        except Exception:
            return "⚠️ Ошибка локальной модели."
