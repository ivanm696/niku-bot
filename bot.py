import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from groq import Groq

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    if not BOT_TOKEN or not GROQ_API_KEY:
        raise ValueError("Переменные окружения BOT_TOKEN или GROQ_API_KEY не заданы!")
except Exception as e:
    logging.error('Критическая ошибка загрузки конфигов: %s', e)
    raise

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY)

# Контекст общения пользователей
user_context = {}


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_context[message.from_user.id] = []
    await message.answer(
        "🤖 Привет! Я NicuAI. Модель обновлена на актуальную Llama-3.3-70b-versatile.\n"
        "Задай мне любой вопрос!"
    )


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_context:
        user_context[user_id] = []

    # Записываем реплику пользователя
    user_context[user_id].append({"role": "user", "content": message.text})

    # Ограничиваем контекст (последние 20 сообщений)
    if len(user_context[user_id]) > 20:
        user_context[user_id] = user_context[user_id][-20:]

    # Имитация набора текста в Телеграмме
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )

    try:
        system_prompt = {
            "role": "system",
            "content": "You are NicuAI, a helpful AI assistant."
        }
        messages_to_send = [system_prompt] + user_context[user_id]

        # Вызываем рабочую модель
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_to_send,
            temperature=0.7
        )

        bot_response = completion.choices[0].message.content
        
        # Сохраняем ответ в память бота
        user_context[user_id].append({"role": "assistant", "content": bot_response})

        # Отправляем чистый текст
        await message.answer(bot_response)

    except Exception as e:
        logger.error(f"Ошибка при вызове Groq API: {e}")
        await message.answer(f"⚠️ Ошибка вызова Groq API: {str(e)}")


async def main():
    logger.info("Принудительно очищаем старые вебхуки...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Запуск чистого Long Polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
