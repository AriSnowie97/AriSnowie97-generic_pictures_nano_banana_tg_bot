"""
Gemini API service wrapper.
Handles both text-to-image and image-to-image generation.
"""

import asyncio
import io
import logging
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from PIL import Image

from config import GOOGLE_API_KEY, MODELS

logger = logging.getLogger(__name__)

# Configure Gemini API key once at import time
genai.configure(api_key=GOOGLE_API_KEY)

# Retry config for 429 rate-limit errors
_MAX_RETRIES = 3
_RETRY_DELAYS = [5, 15, 30]   # seconds between retries


class GeminiService:
    """Wrapper around Google Generative AI for image generation."""

    # ── Text-to-image ─────────────────────────────────────────────────────────

    async def generate_image_from_text(
        self,
        prompt: str,
        model_id: str,
        aspect_ratio: str = "1:1",
    ) -> tuple[bytes, str]:
        """
        Generate an image from a text prompt.

        Returns:
            (image_bytes, mime_type) tuple
        Raises:
            RuntimeError on API failure or no image in response
        """
        model_info = MODELS[model_id]

        if model_info["provider"] == "imagen":
            return await self._generate_imagen(prompt, aspect_ratio, model_id=model_id)
        else:
            return await self._generate_gemini_flash(prompt, aspect_ratio, model_id=model_id)

    # ── Image-to-image ────────────────────────────────────────────────────────

    async def generate_image_from_reference(
        self,
        prompt: str,
        reference_image_bytes: bytes,
        model_id: str,
        aspect_ratio: str = "1:1",
    ) -> tuple[bytes, str]:
        """
        Generate / edit an image using a reference photo + text prompt.

        Returns:
            (image_bytes, mime_type) tuple
        Raises:
            RuntimeError if model doesn't support image input or API fails
        """
        model_info = MODELS[model_id]
        if not model_info["supports_image_input"]:
            raise RuntimeError(
                f"Модель {model_id} не поддерживает входные изображения. "
                "Выбери Gemini 2.0 Flash для работы с фото-референсом."
            )
        return await self._generate_gemini_flash(
            prompt, aspect_ratio, model_id=model_id, reference_image_bytes=reference_image_bytes
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _generate_gemini_flash(
        self,
        prompt: str,
        aspect_ratio: str,
        model_id: str = "gemini-2.5-flash-image",
        reference_image_bytes: Optional[bytes] = None,
    ) -> tuple[bytes, str]:
        """Call any Gemini image generation model with auto-retry on 429."""
        model = genai.GenerativeModel(model_id)

        ar_hint = self._aspect_ratio_hint(aspect_ratio)
        full_prompt = f"{prompt}\n\n{ar_hint}" if ar_hint else prompt

        contents: list = []
        if reference_image_bytes:
            ref_image = self._resize_image(reference_image_bytes)
            contents.append(ref_image)
        contents.append(full_prompt)

        last_error: Exception = RuntimeError("Unknown error")
        for attempt, delay in enumerate([0] + _RETRY_DELAYS, start=0):
            if delay:
                logger.info(f"Rate limit hit, retrying in {delay}s (attempt {attempt}/{_MAX_RETRIES})...")
                await asyncio.sleep(delay)
            try:
                response: GenerateContentResponse = await model.generate_content_async(contents)
                return self._extract_image_from_response(response)
            except Exception as e:
                last_error = e
                if _is_rate_limit(e) and attempt < _MAX_RETRIES:
                    continue
                raise
        raise last_error

    async def _generate_imagen(
        self, prompt: str, aspect_ratio: str, model_id: str = "imagen-4.0-generate-001"
    ) -> tuple[bytes, str]:
        """Call Imagen 4 (or any Imagen model) with auto-retry on 429."""
        imagen_model = genai.ImageGenerationModel(model_id)

        last_error: Exception = RuntimeError("Unknown error")
        for attempt, delay in enumerate([0] + _RETRY_DELAYS, start=0):
            if delay:
                logger.info(f"Rate limit hit, retrying Imagen in {delay}s (attempt {attempt}/{_MAX_RETRIES})...")
                await asyncio.sleep(delay)
            try:
                result = await imagen_model.generate_images_async(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult",
                )
                break
            except Exception as e:
                last_error = e
                if _is_rate_limit(e) and attempt < _MAX_RETRIES:
                    continue
                raise
        else:
            raise last_error

        if not result.images:
            raise RuntimeError(
                "Imagen не вернул изображение. "
                "Попробуй изменить промпт или выбрать другую модель."
            )

        img_bytes = result.images[0]._image_bytes  # type: ignore[attr-defined]
        return img_bytes, "image/png"

    # ── Utility ───────────────────────────────────────────────────────────────

    def _extract_image_from_response(
        self, response: GenerateContentResponse
    ) -> tuple[bytes, str]:
        """Pull the first image part out of a Gemini response."""
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith(
                    "image/"
                ):
                    return part.inline_data.data, part.inline_data.mime_type

        raise RuntimeError(
            "Gemini не вернул изображение. "
            "Попробуй другой промпт или переключи модель."
        )

    def _resize_image(self, image_bytes: bytes, max_size: int = 1024) -> Image.Image:
        """Resize image to fit within max_size x max_size, preserving aspect ratio."""
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        return img

    @staticmethod
    def _aspect_ratio_hint(aspect_ratio: str) -> str:
        hints = {
            "1:1":  "Generate a square 1:1 image.",
            "16:9": "Generate a wide landscape 16:9 image.",
            "9:16": "Generate a tall portrait 9:16 image.",
            "4:3":  "Generate a 4:3 image.",
        }
        return hints.get(aspect_ratio, "")


def _is_rate_limit(exc: Exception) -> bool:
    """Return True if the exception is a 429 / quota-exceeded error."""
    msg = str(exc).lower()
    return any(kw in msg for kw in ("429", "resource_exhausted", "quota", "rate limit", "too many"))
