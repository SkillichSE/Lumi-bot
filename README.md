# Lumi bot

<img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/377255ad-beec-45ee-b631-b9f7e1eea769" />

A Telegram **bot** integrated with a local LLM (LM Studio).  
Responds to messages, remembers chat history, and speaks in different moods. Triggered by the name **“Lumi”**.
## User-facing messages: **Russian**
![Image](https://github.com/user-attachments/assets/3ce9da92-3388-44bb-8b5f-8f02a46e442b)
---
## Features

- Local AI replies via LM Studio (`llama-3.1-8b-instruct`)
- <img width="990" height="209" alt="Image" src="https://github.com/user-attachments/assets/5fe92dca-e033-45b3-8985-fea37bd7a664" />
- Chat memory per conversation
- <img width="392" height="243" alt="Image" src="https://github.com/user-attachments/assets/527b42fd-9e24-4ac4-a409-45efddb6a001" />
- Multiple moods (friendly, sarcastic, formal, funny, aggressive, horny, uncensored, shy)
- <img width="702" height="551" alt="Image" src="https://github.com/user-attachments/assets/50d58138-2dd3-4f41-bca5-149a9e72b2b8" />
- Commands for memory and bot management
- <img width="624" height="243" alt="Image" src="https://github.com/user-attachments/assets/f47ec303-9323-4f10-9791-eea932d35ea1" />  
- Owner-only reset command
- <img width="588" height="295" alt="Image" src="https://github.com/user-attachments/assets/8185d2ef-34f4-47c9-aacd-80217a697187" />  

---

## Installation

1. **Clone the repo:**  
```bash
git clone <repo_url>
cd lumi-bot
```

2. **Create a virtual environment and install dependencies:**  
```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

```

3. **Copy `.example.env` to `.env` and fill in your data:**  
```env
TG_API_ID=12345678
TG_API_HASH="1234567890"
BOT_TOKEN="1234567890:ABCDEF..."
OWNER_ID=1212121212
HISTORY_MAX=10
```

4. **Run the bot:**  
```bash
python bot.py
```

> Make sure **LM Studio** is running at `http://localhost:1234`.

---

## Commands

**General:**

- `/lumi` — info and project links  
- `/commands` — command reference  
- `/ping` — check response time  
- `/model` — show active model  
- `/prompt` — show system prompt (*lot of text!*) 

**Memory:**

- `/memorize <text>` — save a note  
- `/show_memory` — list saved notes  
- `/forget` — delete all notes  
- `/forget <number>` — delete a single note  

**Moods:**

- `/mood` — show current mood  
- `/mood <mood>` — set mood (friendly, sarcastic, formal, funny, aggressive, horny, uncensored, shy)  
- `/mood list` — list available moods  

**Owner-only (OWNER_ID):**

- `/reset` — clear chat memory, history, and reset mood  

---

## LM Studio Settings

- Default API: `http://localhost:1234/v1/chat/completions`  
- Default model: `llama-3.1-8b-instruct`  
- Request timeout: 60s  

---

## Notes

- User-facing messages: **Russian**  
- Developer comments, README, and instructions: **English**
- **HISTORY_MAX** can be adjusted in .env to change how many last messages are included in AI context
- `PROJECT_LINKS` in code can be changed for your own references  
# Also try <a href="https://github.com/SkillichSE/Lumi-userbot">userbot version</a>













