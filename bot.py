import os
import json
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Ты — Нику (Nicu), умный и дружелюбный AI ассистент в Telegram.
Ты создан ivanm696 и работаешь на базе Groq llama-3.3-70b.
Отвечай на языке пользователя (русский, молдавский, английский, румынский).
Будь полезным, кратким и дружелюбным. Можешь помогать с кодом, вопросами, переводами."""

# In-memory chat history per user (last 20 messages)
histories: dict[int, list[dict]] = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def ask_groq(user_id: int, user_text: str) -> str:
    if user_id not in histories:
        histories[user_id] = []

    histories[user_id].append({"role": "user", "content": user_text})

    # Keep last 20 messages
    if len(histories[user_id]) > 20:
        histories[user_id] = histories[user_id][-20:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + histories[user_id]

    async with aiohttp.ClientSession() as session:
        async with session.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }
        ) as resp:
            data = await resp.json()
            reply = data["choices"][0]["message"]["content"]
            histories[user_id].append({"role": "assistant", "content": reply})
            return reply

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    histories.pop(msg.from_user.id, None)
    await msg.answer(
        "👋 Бунэ! Ям Нику — ассистентул тэу AI!\n\n"
        "Скрие-мь орице — те вой ажута 🤖\n\n"
        "Привет! Я Нику, твой AI ассистент.\n"
        "Пиши мне что угодно — помогу! 💬\n\n"
        "Hi! I'm Nicu, your AI assistant.\n"
        "Ask me anything! 🌟"
    )

@dp.message(Command("reset"))
async def cmd_reset(msg: Message):
    histories.pop(msg.from_user.id, None)
    await msg.answer("🔄 Диалог сброшен! / Dialog resetat! / Conversation reset!")

@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "🤖 <b>Нику — AI Ассистент</b>\n\n"
        "<b>Команды:</b>\n"
        "/start — начать / начэ / start\n"
        "/reset — сбросить диалог\n"
        "/help — помощь\n\n"
        "<b>Возможности:</b>\n"
        "• Отвечаю на любые вопросы\n"
        "• Помогаю с кодом\n"
        "• Перевожу тексты\n"
        "• Помню контекст разговора\n"
        "• Русский, молдавский, английский, румынский",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def handle_message(msg: Message):
    await msg.bot.send_chat_action(msg.chat.id, "typing")
    try:
        reply = await ask_groq(msg.from_user.id, msg.text)
        # Split long messages
        if len(reply) > 4000:
            for i in range(0, len(reply), 4000):
                await msg.answer(reply[i:i+4000])
        else:
            await msg.answer(reply)
    except Exception as e:
        await msg.answer(f"⚠️ Ероаре / Ошибка: {str(e)[:100]}")

async def main():
    print("🚀 Nicu bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
