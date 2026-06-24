# 🍌✨ NanoBanana — AI Image Generator Bot

Telegram-бот для генерации изображений с помощью Google Gemini API.

## Функционал

- 🖼 **Text-to-Image** — генерация картинок по текстовому промпту
- 📸 **Image-to-Image** — редактирование/стилизация фото по промпту
- 🤖 **Несколько моделей** — Gemini 2.0 Flash + Imagen 3
- 📐 **Соотношение сторон** — 1:1, 16:9, 9:16, 4:3
- 🔄 **Перегенерация** — кнопка для повтора с новым seed

## Быстрый старт (локально)

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать .env файл
cp .env.example .env
# Отредактируй .env — вставь TELEGRAM_BOT_TOKEN и GOOGLE_API_KEY

# 3. Запустить бота
python bot.py
```

## Деплой на Railway

### Вариант A — через Railway CLI

```bash
# Установить Railway CLI
npm install -g @railway/cli

# Войти в аккаунт
railway login

# Создать новый проект
railway init

# Задать переменные окружения
railway variables set TELEGRAM_BOT_TOKEN=<твой_токен>
railway variables set GOOGLE_API_KEY=<твой_api_ключ>

# Получить публичный URL проекта и задать как WEBHOOK_URL
# Формат: https://<название>.up.railway.app
railway variables set WEBHOOK_URL=https://<твой-проект>.up.railway.app

# Задеплоить
railway up
```

### Вариант B — через GitHub

1. Загрузи проект на GitHub
2. На [railway.app](https://railway.app) создай новый проект из GitHub репозитория
3. Добавь переменные окружения в настройках проекта:
   - `TELEGRAM_BOT_TOKEN`
   - `GOOGLE_API_KEY`
   - `WEBHOOK_URL` (URL твоего Railway сервиса)
4. Railway автоматически задеплоит бота

## Переменные окружения

| Переменная | Описание | Обязательна |
|-----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Токен от @BotFather | ✅ |
| `GOOGLE_API_KEY` | Ключ Google AI Studio | ✅ |
| `WEBHOOK_URL` | Публичный URL (Railway даст автоматически) | Для продакшена |
| `PORT` | Порт сервера (Railway ставит автоматически) | Нет |

## Получение API-ключей

- **Telegram Bot Token**: напиши [@BotFather](https://t.me/BotFather) → /newbot
- **Google AI API Key**: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и инструкция |
| `/generate <промпт>` | Генерация по тексту |
| `/model` | Выбор AI-модели |
| `/ratio` | Соотношение сторон |
| `/help` | Справка |
