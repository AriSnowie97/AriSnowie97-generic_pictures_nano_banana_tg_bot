"""
Shared user state store (in-memory, per chat_id).
Holds: current model, aspect ratio, last prompt, pending photo bytes.
"""
from config import DEFAULT_MODEL, DEFAULT_ASPECT_RATIO

# chat_id -> dict
_state: dict[int, dict] = {}


def get_state(chat_id: int) -> dict:
    if chat_id not in _state:
        _state[chat_id] = {
            "model": DEFAULT_MODEL,
            "aspect_ratio": DEFAULT_ASPECT_RATIO,
            "last_prompt": None,
            "pending_photo": None,      # bytes | None — photo waiting for prompt
        }
    return _state[chat_id]


def set_model(chat_id: int, model_id: str) -> None:
    get_state(chat_id)["model"] = model_id


def set_aspect_ratio(chat_id: int, ar: str) -> None:
    get_state(chat_id)["aspect_ratio"] = ar


def set_last_prompt(chat_id: int, prompt: str) -> None:
    get_state(chat_id)["last_prompt"] = prompt


def set_pending_photo(chat_id: int, photo_bytes: bytes | None) -> None:
    get_state(chat_id)["pending_photo"] = photo_bytes
