import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, html
from aiogram.filters import CommandStart, Command
from groq import Groq

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация токенов
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("Криcritical Ошибка: Проверь BOT_TOKEN и GROQ_API_KEY в настройках Render!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY)

# Хранилище контекста (память бота: user_id -> список сообщений)
# Хранит до 20 сообщений, как заявлено в твоем README
MAX_CONTEXT = 20
user_context = {}

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_context[message.from_user.id] = [] # Сброс памяти при старте
    await message.answer(
        "🤖 **Привет! Я NicuAI** — твой умный ассистент на базе Llama-3.3-70b.\n\n"
        "💬 Я говорю на русском, молдавском, румынском и английском.\n"
        "💻 Могу помочь с кодом или ответить на любой вопрос.\n"
        "🔄 Команда `/reset` очистит нашу память."
    )

@dp.message(Command("reset"))
async def cmd_reset(message: types.Message):
    user_context[message.from_user.id] = []
    await message.answer("🧹 Контекст нашего диалога успешно сброшен!")

@dp.message()
async def handle_groq_ai(message: types.Message):
    user_id = message.from_user.id
    
    # Инициализируем контекст для нового пользователя
    if user_id not in user_context:
        user_context[user_id] = []
        
    # Добавляем текущее сообщение пользователя в историю
    user_context[user_id].append({"role": "user", "content": message.text})
    
    # Обрезаем контекст, если он превысил лимит в 20 сообщений
    if len(user_context[user_id]) > MAX_CONTEXT:
        user_context[user_id] = user_context[user_id][-MAX_CONTEXT:]

    # Показываем статус "печатает..."
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Системный промпт, чтобы бот знал, кто он
        system_prompt = {"role": "system", "content": "You are NicuAI, a helpful assistant. You speak Russian, Moldovan, Romanian, and English. Help with coding and questions efficiently."}
        messages_to_send = [system_prompt] + user_context[user_id]

        # Запрос к Groq API
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_to_send,
            temperature=0.7,
            max_tokens=2048
        )
        
        bot_response = completion.choices[0].message.content
        
        # Добавляем ответ бота в память
        user_context[user_id].append({"role": "assistant", "content": bot_response})
        
        # Отправляем ответ пользователю
        await message.answer(bot_response)

    except Exception as e:
        logging.error(f"Ошибка вызова Groq API: {e}")
        await message.answer("⚠️ Произошла ошибка при обращении к ИИ-движку Groq. Попробуй позже.")

async def main():
    logging.info("Запуск полноценного NicuAI движка...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
