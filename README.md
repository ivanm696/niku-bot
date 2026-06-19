# Nicu Bot 🤖

AI ассистент в Telegram на базе Groq llama-3.3-70b.

**Бот:** [@Niku_bot](https://t.me/Niku_bot)

## Возможности
- 💬 Отвечает на любые вопросы
- 🧠 Помнит контекст разговора (20 сообщений)
- 🌍 Русский, молдавский, английский, румынский
- 💻 Помогает с кодом
- 🔄 /reset — сбросить диалог

## Деплой на Railway

1. Fork этого репо
2. Зайди на [railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Добавь переменные окружения:
   - `BOT_TOKEN` = токен от @BotFather
   - `GROQ_API_KEY` = ключ от console.groq.com
5. Deploy!

## Локальный запуск

```bash
pip install -r requirements.txt
export BOT_TOKEN=your_token
export GROQ_API_KEY=your_groq_key
python bot.py
```

## Стек
- [aiogram 3.x](https://aiogram.dev/) — Telegram Bot framework
- [Groq](https://console.groq.com) — бесплатный LLM API
- [llama-3.3-70b-versatile](https://groq.com) — языковая модель
