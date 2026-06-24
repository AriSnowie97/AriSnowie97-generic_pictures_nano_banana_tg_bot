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
    # ── Nano Banana (Gemini Image) ─────────────────────────
    "gemini-2.5-flash-image": {
        "label": "🍌 Nano Banana (FREE)",
        "description": "Базовая модель — быстрая генерация и редактирование по фото",
        "supports_image_input": True,
        "provider": "gemini",
        "paid": False,
    },
    "gemini-3.1-flash-image": {
        "label": "🍌🍌 Nano Banana 2 (Paid)",
        "description": "Gemini 3.1 Flash Image — визуальный интеллект профи-уровня",
        "supports_image_input": True,
        "provider": "gemini",
        "paid": True,
    },
    "gemini-3-pro-image": {
        "label": "👑 Nano Banana Pro (Paid)",
        "description": "Gemini 3 Pro Image — топовое качество генерации",
        "supports_image_input": True,
        "provider": "gemini",
        "paid": True,
    },
    # ── Imagen 4 ───────────────────────────────────────────
    "imagen-4.0-generate-001": {
        "label": "🎨 Imagen 4 (Paid)",
        "description": "Лучший рендеринг текста и высокое качество (только текст→фото)",
        "supports_image_input": False,
        "provider": "imagen",
        "paid": True,
    },
    "imagen-4.0-ultra-generate-001": {
        "label": "💎 Imagen 4 Ultra (Paid)",
        "description": "Максимальное качество Imagen — для сложных сцен (только текст→фото)",
        "supports_image_input": False,
        "provider": "imagen",
        "paid": True,
    },
}

DEFAULT_MODEL: str = "gemini-2.5-flash-image"

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
