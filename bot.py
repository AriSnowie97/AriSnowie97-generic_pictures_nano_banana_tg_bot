"""
NanoBanana — Telegram Image Generation Bot
Powered by Google Gemini API

Entry point. Sets up the bot, registers handlers, and starts either:
  - Webhook mode (production / Railway)
  - Long polling mode (local development)
"""

import asyncio
import logging
import os
import sys

from telegram import BotCommand
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, PORT
from handlers import (
    start_handler,
    help_handler,
    text_message_handler,
    generate_command_handler,
    photo_handler,
    callback_handler,
    model_command_handler,
    ratio_command_handler,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def set_commands(app: Application) -> None:
    """Register bot commands visible in Telegram UI."""
    await app.bot.set_my_commands([
        BotCommand("start",    "🚀 Начать работу"),
        BotCommand("generate", "🖼 Генерировать по тексту"),
        BotCommand("model",    "🤖 Выбрать AI-модель"),
        BotCommand("ratio",    "📐 Соотношение сторон"),
        BotCommand("help",     "❓ Справка"),
    ])


def build_app() -> Application:
    """Build and configure the Telegram Application."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ── Command handlers ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start",    start_handler))
    app.add_handler(CommandHandler("help",     help_handler))
    app.add_handler(CommandHandler("generate", generate_command_handler))
    app.add_handler(CommandHandler("model",    model_command_handler))
    app.add_handler(CommandHandler("ratio",    ratio_command_handler))

    # ── Message handlers ───────────────────────────────────────────────────────
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
    )

    # ── Inline button handler ──────────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(callback_handler))

    return app


async def main() -> None:
    app = build_app()

    # Register bot commands in Telegram menu
    await set_commands(app)

    if WEBHOOK_URL:
        # ── Webhook mode (Railway / production) ──────────────────────────────
        webhook_path = f"/webhook/{TELEGRAM_BOT_TOKEN}"
        full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"

        logger.info(f"Starting webhook on port {PORT} → {full_webhook_url}")

        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=full_webhook_url,
            drop_pending_updates=True,
        )
    else:
        # ── Polling mode (local development) ─────────────────────────────────
        logger.info("Starting long polling (local mode)...")
        await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
