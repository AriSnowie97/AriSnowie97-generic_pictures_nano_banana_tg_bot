"""
/start and /help command handlers.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import MODELS, DEFAULT_MODEL
from keyboards import model_keyboard, aspect_ratio_keyboard
from state import get_state

logger = logging.getLogger(__name__)

WELCOME_TEXT = """
🍌✨ *Привет! Я NanoBanana — бот-генератор изображений на базе Google Gemini!*

*Что я умею:*
• 🖼 Генерировать картинки по текстовому описанию
• 📸 Создавать картинки на основе твоего фото + промпта
• 🎨 Работать с несколькими AI-моделями
• 📐 Менять соотношение сторон (1:1, 16:9, 9:16, 4:3)

*Как пользоваться:*
1️⃣ Просто напиши, что хочешь сгенерировать
   _Пример: нарисуй котика в космосе в стиле аниме_

2️⃣ Или отправь фото с подписью
   _Отправь любое фото + напиши что хочешь сделать с ним_

*Команды:*
/generate — генерация по тексту
/model — выбор AI-модели
/ratio — соотношение сторон
/help — эта справка

Поехали! 🚀
"""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=model_keyboard(),
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    state = get_state(update.effective_chat.id)
    current_model = MODELS[state["model"]]["label"]
    current_ar = state["aspect_ratio"]

    help_text = f"""
{WELCOME_TEXT}

⚙️ *Текущие настройки:*
• Модель: {current_model}
• Соотношение сторон: {current_ar}
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")
