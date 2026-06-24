import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables!")

# ── Google Gemini ─────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in environment variables!")

# ── Webhook / Polling ─────────────────────────────────────
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
PORT: int = int(os.getenv("PORT", "8080"))

# ── Available models ──────────────────────────────────────
MODELS: dict[str, dict] = {
    "gemini-2.0-flash-preview-image-generation": {
        "label": "✨ Gemini 2.0 Flash (Image Gen)",
        "description": "Быстрая генерация + редактирование по референсу",
        "supports_image_input": True,
        "provider": "gemini",
    },
    "imagen-3.0-generate-002": {
        "label": "🎨 Imagen 3",
        "description": "Высококачественная генерация (только текст)",
        "supports_image_input": False,
        "provider": "imagen",
    },
}

DEFAULT_MODEL: str = "gemini-2.0-flash-preview-image-generation"

# ── Aspect ratios ─────────────────────────────────────────
ASPECT_RATIOS: dict[str, dict] = {
    "1:1":  {"label": "⬜ 1:1 (квадрат)",     "width": 1024, "height": 1024},
    "16:9": {"label": "📺 16:9 (горизонт.)",  "width": 1344, "height": 768},
    "9:16": {"label": "📱 9:16 (вертикаль)",  "width": 768,  "height": 1344},
    "4:3":  {"label": "🖼️ 4:3 (класс.)",      "width": 1152, "height": 896},
}

DEFAULT_ASPECT_RATIO: str = "1:1"

# ── Misc ──────────────────────────────────────────────────
MAX_PROMPT_LENGTH: int = 4000
