"""
NanoBanana — Telegram Image Generation Bot
Powered by Google Gemini API

Entry point. Sets up the bot, registers handlers, and starts either:
  - Webhook mode (production / Railway with WEBHOOK_URL set)
  - Long polling mode + health-check HTTP server (Railway without WEBHOOK_URL)
"""

import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

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


# ── Health-check server (keeps Railway happy in polling mode) ─────────────────

class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"NanoBanana bot is running!")

    def log_message(self, *args):
        pass  # suppress access logs


def _start_health_server(port: int) -> None:
    """Start a tiny HTTP server in a daemon thread so Railway is happy."""
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    logger.info(f"Health-check server listening on port {port}")


# ── Bot setup ─────────────────────────────────────────────────────────────────

async def _post_init(app: Application) -> None:
    """Called by PTB after the bot is initialized — register menu commands."""
    await app.bot.set_my_commands([
        BotCommand("start",    "Начать работу"),
        BotCommand("generate", "Генерировать по тексту"),
        BotCommand("model",    "Выбрать AI-модель"),
        BotCommand("ratio",    "Соотношение сторон"),
        BotCommand("help",     "Справка"),
    ])
    logger.info("Bot commands registered successfully")


def build_app() -> Application:
    """Build and configure the Telegram Application."""
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(_post_init)          # async setup runs inside PTB's own loop
        .build()
    )

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


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """
    PTB v21: run_polling() and run_webhook() are SYNCHRONOUS — they manage
    the event loop internally. Do NOT call them with 'await' inside asyncio.run().
    """
    app = build_app()

    if WEBHOOK_URL:
        # ── Webhook mode (Railway with WEBHOOK_URL env var set) ───────────────
        webhook_path = f"/webhook/{TELEGRAM_BOT_TOKEN}"
        full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"
        logger.info(f"Starting webhook on port {PORT} -> {full_webhook_url}")

        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=full_webhook_url,
            drop_pending_updates=True,
        )
    else:
        # ── Polling mode (Railway without WEBHOOK_URL, or local dev) ─────────
        logger.info("Starting long polling mode...")
        _start_health_server(PORT)   # keeps Railway from killing the process
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
