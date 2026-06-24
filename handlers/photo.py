"""
Handles incoming photos (with or without caption).
Logic:
  - Photo + caption → immediate image-to-image generation
  - Photo only      → store as pending reference, ask for prompt
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import MAX_PROMPT_LENGTH, MODELS
from handlers.generate import run_generation
from state import get_state, set_pending_photo

logger = logging.getLogger(__name__)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photo messages."""
    chat_id = update.effective_chat.id
    state = get_state(chat_id)
    model_id = state["model"]
    model_info = MODELS[model_id]

    # Download the highest-resolution version of the photo
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    photo_bytes = bytes(photo_bytes)

    caption = (update.message.caption or "").strip()

    if caption:
        # Photo + caption → generate immediately
        if not model_info["supports_image_input"]:
            await update.message.reply_text(
                f"⚠️ Текущая модель *{model_info['label']}* не поддерживает фото-референс.\n"
                f"Автоматически переключаю на *Gemini 2.0 Flash*...",
                parse_mode="Markdown",
            )
            from state import set_model
            set_model(chat_id, "gemini-2.0-flash-preview-image-generation")

        if len(caption) > MAX_PROMPT_LENGTH:
            await update.message.reply_text(
                f"⚠️ Подпись слишком длинная. Максимум {MAX_PROMPT_LENGTH} символов."
            )
            return

        await run_generation(
            update, context,
            prompt=caption,
            reference_image_bytes=photo_bytes,
        )
    else:
        # Photo without caption → store and ask for prompt
        set_pending_photo(chat_id, photo_bytes)
        await update.message.reply_text(
            "📸 *Фото получено!*\n\n"
            "Теперь напиши промпт — что сделать с этим фото?\n\n"
            "_Например: сделай аниме-версию, добавь снег, измени стиль на масляную живопись..._",
            parse_mode="Markdown",
        )
