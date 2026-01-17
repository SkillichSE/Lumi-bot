# Utilities for chat memory management

import json
from pathlib import Path
from config import MEMORY_DIR

def get_memory_file(chat_id: int) -> Path:
    """Return the path to the memory file for a chat."""
    path = MEMORY_DIR / f"chat_{chat_id}.json"
    if not path.exists():
        path.write_text(json.dumps({"notes": []}, ensure_ascii=False, indent=2))
    return path

def load_memory(chat_id: int) -> dict:
    """Load the memory of a chat."""
    path = get_memory_file(chat_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"notes": []}

def save_memory(chat_id: int, data: dict):
    """Save memory of a chat."""
    path = get_memory_file(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_note(chat_id: int, text: str):
    """Add a note to chat memory."""
    memory = load_memory(chat_id)
    memory["notes"].append(text)
    # Limit notes to last 50
    if len(memory["notes"]) > 50:
        memory["notes"] = memory["notes"][-50:]
    save_memory(chat_id, memory)

def get_notes(chat_id: int) -> list:
    """Return all notes of the chat."""
    memory = load_memory(chat_id)
    return memory.get("notes", [])

def clear_memory(chat_id: int):
    """Clear all notes of the chat."""
    save_memory(chat_id, {"notes": []})
