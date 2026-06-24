"""
Core generation logic — used by both text and photo handlers.
Handles the full lifecycle: typing indicator → API call → send photo → keyboard.
"""
import io
import logging
from typing import Optional

from telegram import Update, Message
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from config import MODELS
from keyboards import post_generation_keyboard
from services.gemini import GeminiService
from state import get_state, set_last_prompt, set_pending_photo

logger = logging.getLogger(__name__)
gemini = GeminiService()


async def run_generation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    prompt: str,
    reference_image_bytes: Optional[bytes] = None,
    reply_to: Optional[Message] = None,
) -> None:
    """
    Core generation runner.
    - Sends typing/upload indicator
    - Calls Gemini API
    - Sends resulting photo back to the user
    - Attaches post-generation keyboard
    """
    chat_id = update.effective_chat.id
    state = get_state(chat_id)
    model_id = state["model"]
    aspect_ratio = state["aspect_ratio"]

    target_message = reply_to or update.message

    # Persist last prompt for re-generation
    set_last_prompt(chat_id, prompt)

    # Show activity indicator
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

    # Send a "thinking" status message
    status_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏳ Генерирую картинку...\n\n"
             f"🤖 *Модель:* {MODELS[model_id]['label']}\n"
             f"📐 *Соотношение:* {aspect_ratio}\n"
             f"💬 *Промпт:* _{prompt[:100]}{'...' if len(prompt) > 100 else ''}_",
        parse_mode="Markdown",
    )

    try:
        if reference_image_bytes:
            img_bytes, mime_type = await gemini.generate_image_from_reference(
                prompt=prompt,
                reference_image_bytes=reference_image_bytes,
                model_id=model_id,
                aspect_ratio=aspect_ratio,
            )
        else:
            img_bytes, mime_type = await gemini.generate_image_from_text(
                prompt=prompt,
                model_id=model_id,
                aspect_ratio=aspect_ratio,
            )

        # Delete status message before sending photo
        await status_msg.delete()

        caption = (
            f"✅ *Готово!*\n\n"
            f"💬 _{prompt[:200]}{'...' if len(prompt) > 200 else ''}_\n\n"
            f"🤖 {MODELS[model_id]['label']} • 📐 {aspect_ratio}"
        )

        await context.bot.send_photo(
            chat_id=chat_id,
            photo=io.BytesIO(img_bytes),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=post_generation_keyboard(prompt),
        )

    except Exception as e:
        logger.error(f"Generation error for chat {chat_id}: {e}", exc_info=True)
        error_text = str(e)

        await status_msg.edit_text(
            f"❌ *Ошибка генерации*\n\n"
            f"{_friendly_error(error_text)}",
            parse_mode="Markdown",
        )


def _friendly_error(raw: str) -> str:
    """Convert raw API errors to user-friendly messages."""
    raw_lower = raw.lower()
    if "safety" in raw_lower or "block" in raw_lower:
        return (
            "🚫 Запрос заблокирован фильтрами безопасности.\n"
            "Попробуй переформулировать промпт."
        )
    if "quota" in raw_lower or "rate" in raw_lower or "429" in raw_lower:
        return (
            "⏱ Превышен лимит запросов.\n"
            "Подожди немного и попробуй снова."
        )
    if "image input" in raw_lower or "не поддерживает входные" in raw_lower:
        return (
            "⚠️ Выбранная модель не поддерживает фото-референс.\n"
            "Переключись на *Gemini 2.0 Flash* через /model"
        )
    if "api key" in raw_lower or "invalid" in raw_lower:
        return "🔑 Проблема с API-ключом. Свяжись с администратором."
    return f"Что-то пошло не так:\n`{raw[:300]}`"
