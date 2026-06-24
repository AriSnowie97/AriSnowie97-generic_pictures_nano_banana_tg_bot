"""
Callback query handler — handles all inline button presses.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import MODELS, ASPECT_RATIOS
from keyboards import model_keyboard, aspect_ratio_keyboard, post_generation_keyboard
from state import get_state, set_model, set_aspect_ratio

logger = logging.getLogger(__name__)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callback_data to the correct action."""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    data: str = query.data

    # ── Model selection ────────────────────────────────────────────────────────
    if data.startswith("model:"):
        model_id = data.split(":", 1)[1]
        if model_id not in MODELS:
            await query.answer("Неизвестная модель!", show_alert=True)
            return

        set_model(chat_id, model_id)
        model_info = MODELS[model_id]
        await query.edit_message_text(
            f"✅ *Модель выбрана:* {model_info['label']}\n\n"
            f"_{model_info['description']}_\n\n"
            f"{'📸 Поддерживает фото-референс!' if model_info['supports_image_input'] else '📝 Только текстовая генерация'}",
            parse_mode="Markdown",
        )

    # ── Aspect ratio selection ─────────────────────────────────────────────────
    elif data.startswith("ar:"):
        ar = data.split(":", 1)[1]
        if ar not in ASPECT_RATIOS:
            await query.answer("Неизвестное соотношение!", show_alert=True)
            return

        set_aspect_ratio(chat_id, ar)
        ar_info = ASPECT_RATIOS[ar]
        await query.edit_message_text(
            f"✅ *Соотношение сторон:* {ar_info['label']}\n\n"
            f"Теперь все картинки будут генерироваться в формате *{ar}*",
            parse_mode="Markdown",
        )

    # ── Re-generation ──────────────────────────────────────────────────────────
    elif data == "regen":
        state = get_state(chat_id)
        last_prompt = state.get("last_prompt")
        if not last_prompt:
            await query.answer("Нет сохранённого промпта для перегенерации!", show_alert=True)
            return

        await query.answer("🔄 Перегенерирую...")
        # Create a fake update to reuse run_generation
        from handlers.generate import run_generation
        await run_generation(update, context, prompt=last_prompt)

    # ── Show model keyboard ────────────────────────────────────────────────────
    elif data == "show_models":
        state = get_state(chat_id)
        current = MODELS[state["model"]]["label"]
        await query.edit_message_text(
            f"🤖 *Выбор модели*\n\nСейчас: *{current}*\n\nВыбери модель:",
            parse_mode="Markdown",
            reply_markup=model_keyboard(),
        )

    # ── Show aspect ratio keyboard ─────────────────────────────────────────────
    elif data == "show_ar":
        state = get_state(chat_id)
        current_ar = state["aspect_ratio"]
        await query.edit_message_text(
            f"📐 *Соотношение сторон*\n\nСейчас: *{current_ar}*\n\nВыбери формат:",
            parse_mode="Markdown",
            reply_markup=aspect_ratio_keyboard(),
        )

    else:
        logger.warning(f"Unknown callback data: {data}")
        await query.answer("Неизвестное действие", show_alert=True)


async def model_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /model command — show model selection keyboard."""
    chat_id = update.effective_chat.id
    state = get_state(chat_id)
    current = MODELS[state["model"]]["label"]
    await update.message.reply_text(
        f"🤖 *Выбор AI-модели*\n\nТекущая модель: *{current}*\n\nВыбери модель для генерации:",
        parse_mode="Markdown",
        reply_markup=model_keyboard(),
    )


async def ratio_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ratio command — show aspect ratio keyboard."""
    chat_id = update.effective_chat.id
    state = get_state(chat_id)
    current_ar = state["aspect_ratio"]
    await update.message.reply_text(
        f"📐 *Соотношение сторон*\n\nТекущее: *{current_ar}*\n\nВыбери формат для генерации:",
        parse_mode="Markdown",
        reply_markup=aspect_ratio_keyboard(),
    )
