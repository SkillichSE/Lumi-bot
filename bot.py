# bot.py
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from config import BOT_TOKEN, OWNER_ID, HISTORY_MAX, DEFAULT_MOOD, MOOD_PROMPTS, MODEL_NAME
from utils.logging_setup import full_logger, error_logger
from utils.memory import add_note, get_notes, clear_memory
from utils.lm import ask_model
from html import escape

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Chat history and moods
HISTORY = {}
MODEL_MOOD = {} 
CHAT_USERS = {}  


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я <b>Люми</b> — умный ассистент 💜\n"
        "Напиши <code>люми</code>, чтобы поговорить со мной.\n\n"
        "<a href='https://t.me/LumiAsk_bot?start=1'>📖 Помощь и команды</a>",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("lumi"))
async def lumi_info(message: types.Message):
    await message.answer(
        "<b>Проект Lumi Userbot</b>\n"
        "💻 Local LLM assistant\n"
        "📖 https://t.me/LumiAsk_bot?start=1",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("commands"))
async def commands(message: types.Message):
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
        "/reset — owner-only reset",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("ping"))
async def ping(message: types.Message):
    import time
    start = time.perf_counter()
    msg = await message.answer("🏓 Ping…", parse_mode=ParseMode.HTML)
    elapsed = round((time.perf_counter() - start) * 1000, 1)
    await msg.edit_text(f"🏓 Pong! {elapsed} ms", parse_mode=ParseMode.HTML)

@dp.message(Command("model"))
async def model_cmd(message: types.Message):
    await message.answer(f"🤖 Модель: {MODEL_NAME}", parse_mode=ParseMode.HTML)

@dp.message(Command("prompt"))
async def prompt_cmd(message: types.Message):
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
    await message.answer(f"<pre>{system_content}</pre>", parse_mode=ParseMode.HTML)


@dp.message(lambda m: m.text and m.text.lower().startswith("/memorize "))
async def memorize(message: types.Message):
    chat_id = message.chat.id
    text = message.text[10:].strip()
    if not text:
        await message.reply("❌ Напиши что запомнить: /memorize <текст>", parse_mode=ParseMode.HTML)
        return
    add_note(chat_id, text)
    await message.reply(f"💾 Запомнила для чата: {text}", parse_mode=ParseMode.HTML)

@dp.message(Command("show_memory"))
async def show_memory(message: types.Message):
    chat_id = message.chat.id
    notes = get_notes(chat_id)
    if not notes:
        await message.reply("📭 Памяти пока нет.", parse_mode=ParseMode.HTML)
        return
    text = "\n".join(f"{i+1}. {n}" for i, n in enumerate(notes))
    await message.reply(f"🧠 Память чата:\n{text}", parse_mode=ParseMode.HTML)

@dp.message(lambda m: m.text and m.text.lower().startswith("/forget"))
async def forget(message: types.Message):
    chat_id = message.chat.id
    parts = message.text.split()
    if len(parts) == 1:
        clear_memory(chat_id)
        await message.reply("🗑 Память чата полностью очищена.", parse_mode=ParseMode.HTML)
        return
    if len(parts) == 2 and parts[1].isdigit():
        idx = int(parts[1]) - 1
        notes = get_notes(chat_id)
        if 0 <= idx < len(notes):
            removed = notes.pop(idx)
            from utils.memory import save_memory
            save_memory(chat_id, {"notes": notes})
            await message.reply(f"🗑 Удалено: {removed}", parse_mode=ParseMode.HTML)
        else:
            await message.reply("❌ Нет записи с таким номером.", parse_mode=ParseMode.HTML)
        return
    await message.reply("❌ Использование: /forget или /forget <номер>", parse_mode=ParseMode.HTML)


@dp.message(Command("mood"))
async def mood_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text or ""

    args = text[len("/mood"):].strip().lower()

    if not args:
        mood = MODEL_MOOD.get(chat_id, DEFAULT_MOOD)
        await message.reply(
            f"🎭 Текущий режим: {mood}\n"
            "/mood <настроение> — установить настроение\n"
            "/mood list — список доступных настроений"
        )
        return

    if args == "list":
        await message.reply(
            "🎭 Доступные настроения:\n" + ", ".join(MOOD_PROMPTS.keys())
        )
        return

    if args not in MOOD_PROMPTS:
        await message.reply(
            f"❌ Неизвестное настроение.\nДоступные: {', '.join(MOOD_PROMPTS.keys())}"
        )
        return

    MODEL_MOOD[chat_id] = args
    await message.reply(f"✅ Настроение изменено на: {args}")

@dp.message(Command("reset"))
async def reset(message: types.Message):
    chat_id = message.chat.id
    sender_id = message.from_user.id
    if isinstance(OWNER_ID, set):
        allowed = sender_id in OWNER_ID
    else:
        allowed = sender_id == OWNER_ID
    if not allowed:
        await message.reply("❌ Команда доступна только владельцу.", parse_mode=ParseMode.HTML)
        return
    clear_memory(chat_id)
    HISTORY[chat_id] = []
    MODEL_MOOD[chat_id] = DEFAULT_MOOD
    await message.reply("♻️ Полный сброс выполнен: память и история очищены, настроение сброшено.", parse_mode=ParseMode.HTML)


@dp.message()
async def chat_response(message: types.Message):
    chat_id = message.chat.id
    sender_id = message.from_user.id
    username = message.from_user.username or f"user{sender_id}"
    CHAT_USERS[sender_id] = username

    text = message.text.lower()
    respond = "люми" in text

    if chat_id not in HISTORY:
        HISTORY[chat_id] = []
    HISTORY[chat_id].append((username, message.text))
    HISTORY[chat_id] = HISTORY[chat_id][-HISTORY_MAX:]

    if respond:
        try:
            reply_text = await ask_model(
                message.text,
                chat_id,
                sender_id,
                history=HISTORY,
                model_mood=MODEL_MOOD,
                chat_users=CHAT_USERS
            )
            await message.reply(reply_text, parse_mode=ParseMode.HTML)
            full_logger.info(f"{username} ({chat_id}): {message.text}")
            full_logger.info(f"LUMI ({chat_id}): {reply_text}")
        except Exception as e:
            error_logger.exception(f"Error responding: {e}")
            await message.reply("⚠️ Произошла ошибка при обработке сообщения.", parse_mode=ParseMode.HTML)



if __name__ == "__main__":
    print("✅ Lumi bot started.")
    asyncio.run(dp.start_polling(bot))

