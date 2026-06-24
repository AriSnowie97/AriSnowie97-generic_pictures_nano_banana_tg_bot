"""
Handles text messages and /generate command → text-to-image.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import MAX_PROMPT_LENGTH
from handlers.generate import run_generation
from state import get_state, set_pending_photo

logger = logging.getLogger(__name__)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle any plain text message as a generation prompt."""
    chat_id = update.effective_chat.id
    prompt = update.message.text.strip()

    if not prompt:
        await update.message.reply_text("Напиши промпт! 😊")
        return

    if len(prompt) > MAX_PROMPT_LENGTH:
        await update.message.reply_text(
            f"⚠️ Промпт слишком длинный ({len(prompt)} симв.).\n"
            f"Максимум: {MAX_PROMPT_LENGTH} символов."
        )
        return

    # Check if user had previously sent a photo without a prompt
    state = get_state(chat_id)
    pending_photo = state.get("pending_photo")

    if pending_photo:
        # Use the pending photo as reference
        set_pending_photo(chat_id, None)
        await update.message.reply_text(
            "📸 Нашла твоё фото! Генерирую с ним как референсом..."
        )
        await run_generation(
            update, context,
            prompt=prompt,
            reference_image_bytes=pending_photo,
        )
    else:
        await run_generation(update, context, prompt=prompt)


async def generate_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /generate <prompt> command."""
    if context.args:
        prompt = " ".join(context.args).strip()
        await run_generation(update, context, prompt=prompt)
    else:
        await update.message.reply_text(
            "✏️ Напиши промпт после команды:\n"
            "`/generate нарисуй закат над морем в стиле импрессионизма`",
            parse_mode="Markdown",
        )
