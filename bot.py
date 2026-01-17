# Main bot file

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.filters import Command
from config import BOT_TOKEN, OWNER_ID, HISTORY_MAX, DEFAULT_MOOD, MOOD_PROMPTS
from utils.logging_setup import full_logger, error_logger
from utils.memory import add_note, get_notes, clear_memory
from utils.lm import ask_model

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Chat history and moods
HISTORY = {}  # {chat_id: [(username, message)]}
MODEL_MOOD = {}  # {chat_id: mood}
CHAT_USERS = {}  # {user_id: username}

# ---------- Command handlers ----------

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Send greeting and info links."""
    await message.answer(
        "👋 Привет! Я <b>Люми</b> — умный ассистент 💜\n"
        "Напиши <code>люми</code>, чтобы поговорить со мной.\n\n"
        "<a href='https://t.me/LumiAsk_bot?start=1'>📖 Помощь и команды</a>"
    )

@dp.message(Command("lumi"))
async def lumi_info(message: types.Message):
    """Send project info and links."""
    await message.answer(
        "<b>Проект Lumi Userbot</b>\n"
        "💻 Local LLM assistant\n"
        "📖 https://t.me/LumiAsk_bot?start=1"
    )

@dp.message(Command("commands"))
async def commands(message: types.Message):
    """Send command reference."""
    await message.answer(
        "/lumi — info and project links\n"
        "/commands — command reference\n"
        "/ping — check response time\n"
        "/model — show active model\n"
        "/prompt — show system prompt\n"
        "/memorize <text> — save a note\n"
        "/show_memory — list saved notes\n"
        "/forget — delete all notes\n"
        "/forget <number> — delete single note\n"
        "/mood — show current mood\n"
        "/mood <mood> — set mood\n"
        "/mood list — list available moods\n"
        "/reset — owner-only reset"
    )

@dp.message(Command("ping"))
async def ping(message: types.Message):
    """Ping command."""
    import time
    start = time.perf_counter()
    msg = await message.answer("🏓 Ping…")
    elapsed = round((time.perf_counter() - start) * 1000, 1)
    await msg.edit_text(f"🏓 Pong! {elapsed} ms")

@dp.message(Command("model"))
async def model_cmd(message: types.Message):
    """Show active model."""
    from config import MODEL_NAME
    await message.answer(f"🤖 Модель: {MODEL_NAME}")

@dp.message(Command("prompt"))
async def prompt_cmd(message: types.Message):
    """Show system prompt of the chat (long text)."""
    chat_id = message.chat.id
    memory_text = "\n".join(get_notes(chat_id)) or "— нет записей —"
    mood = MODEL_MOOD.get(chat_id, DEFAULT_MOOD)
    mood_text = MOOD_PROMPTS.get(mood, "")
    last_messages = "\n".join(
        f"{username}: {msg}" for username, msg in HISTORY.get(chat_id, [])[-HISTORY_MAX:]
    )
    system_content = f"""
Ты — женская ассистентка Люми. Отвечай кратко и по фактам.

{mood_text}

История чата (последние {HISTORY_MAX} сообщений):
{last_messages}

Записанная память:
{memory_text}
"""
    await message.answer(f"<pre>{system_content}</pre>")

# ---------- Memory commands ----------

@dp.message(lambda m: m.text and m.text.lower().startswith("/memorize "))
async def memorize(message: types.Message):
    """Save a note to chat memory."""
    chat_id = message.chat.id
    text = message.text[10:].strip()
    if not text:
        await message.reply("❌ Напиши что запомнить: /memorize <текст>")
        return
    add_note(chat_id, text)
    await message.reply(f"💾 Запомнила для тебя: {text}")

@dp.message(Command("show_memory"))
async def show_memory(message: types.Message):
    """Show all saved notes."""
    chat_id = message.chat.id
    notes = get_notes(chat_id)
    if not notes:
        await message.reply("📭 Памяти пока нет.")
        return
    text = "\n".join(f"{i+1}. {n}" for i, n in enumerate(notes))
    await message.reply(f"🧠 Память чата:\n{text}")

@dp.message(lambda m: m.text and m.text.lower().startswith("/forget"))
async def forget(message: types.Message):
    """Delete notes: all or by number."""
    chat_id = message.chat.id
    parts = message.text.split()
    if len(parts) == 1:
        clear_memory(chat_id)
        await message.reply("🗑 Память чата полностью очищена.")
        return
    if len(parts) == 2 and parts[1].isdigit():
        idx = int(parts[1]) - 1
        notes = get_notes(chat_id)
        if 0 <= idx < len(notes):
            removed = notes.pop(idx)
            from utils.memory import save_memory
            save_memory(chat_id, {"notes": notes})
            await message.reply(f"🗑 Удалено: {removed}")
        else:
            await message.reply("❌ Нет записи с таким номером.")
        return
    await message.reply("❌ Использование: /forget или /forget <номер>")

# ---------- Mood commands ----------

@dp.message(Command("mood"))
async def mood_show(message: types.Message):
    """Show current mood or list moods."""
    chat_id = message.chat.id
    mood = MODEL_MOOD.get(chat_id, DEFAULT_MOOD)
    await message.reply(
        f"🎭 Текущий режим: {mood}\n"
        f"Использование: /mood <режим>\n/mood list — список режимов"
    )

@dp.message(lambda m: m.text and m.text.lower() == "/mood list")
async def mood_list(message: types.Message):
    """List available moods."""
    await message.reply(f"🎭 Доступные режимы:\n{', '.join(MOOD_PROMPTS.keys())}")

@dp.message(lambda m: m.text and m.text.lower().startswith("/mood "))
async def mood_set(message: types.Message):
    """Set mood of the chat."""
    chat_id = message.chat.id
    mood = message.text[6:].strip().lower()
    if mood not in MOOD_PROMPTS:
        await message.reply(f"❌ Неверное настроение. Доступные: {', '.join(MOOD_PROMPTS.keys())}")
        return
    MODEL_MOOD[chat_id] = mood
    await message.reply(f"✅ Настроение модели для этого чата установлено на: {mood}")

# ---------- Owner-only command ----------

@dp.message(Command("reset"))
async def reset(message: types.Message):
    """Owner-only: reset chat memory, history, and mood."""
    chat_id = message.chat.id
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Команда доступна только владельцу.")
        return
    from utils.memory import clear_memory
    clear_memory(chat_id)
    HISTORY[chat_id] = []
    MODEL_MOOD[chat_id] = DEFAULT_MOOD
    await message.reply("♻️ Полный сброс выполнен: память и история очищены, настроение сброшено.")

# ---------- Chat response ----------

@dp.message()
async def chat_response(message: types.Message):
    """Respond to messages mentioning Lumi or 'люми'."""
    chat_id = message.chat.id
    sender_id = message.from_user.id
    username = message.from_user.username or f"user{sender_id}"
    CHAT_USERS[sender_id] = username

    text = message.text.lower()
    respond = False

    if "люми" in text:
        respond = True

    # Add to history
    if chat_id not in HISTORY:
        HISTORY[chat_id] = []
    HISTORY[chat_id].append((username, message.text))
    HISTORY[chat_id] = HISTORY[chat_id][-HISTORY_MAX:]

    if respond:
        try:
            reply_text = await ask_model(message.text, chat_id, sender_id)
            await message.reply(reply_text)
            full_logger.info(f"{username} ({chat_id}): {message.text}")
            full_logger.info(f"LUMI ({chat_id}): {reply_text}")
        except Exception as e:
            error_logger.exception(f"Error responding: {e}")
            await message.reply("⚠️ Произошла ошибка при обработке сообщения.")

# ---------- Main ----------

async def main():
    """Start bot."""
    print("✅ Lumi bot started.")
    from aiogram import executor
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
