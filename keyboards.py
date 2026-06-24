"""
Keyboard / inline button helpers.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import MODELS, ASPECT_RATIOS


def model_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for model selection."""
    buttons = [
        [InlineKeyboardButton(info["label"], callback_data=f"model:{mid}")]
        for mid, info in MODELS.items()
    ]
    return InlineKeyboardMarkup(buttons)


def aspect_ratio_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for aspect ratio selection."""
    buttons = [
        [InlineKeyboardButton(info["label"], callback_data=f"ar:{ar}")]
        for ar, info in ASPECT_RATIOS.items()
    ]
    return InlineKeyboardMarkup(buttons)


def post_generation_keyboard(prompt: str) -> InlineKeyboardMarkup:
    """Keyboard shown after a successful generation."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Перегенерировать", callback_data="regen"),
            InlineKeyboardButton("📐 Соотношение", callback_data="show_ar"),
        ],
        [
            InlineKeyboardButton("🤖 Сменить модель", callback_data="show_models"),
        ],
    ])
