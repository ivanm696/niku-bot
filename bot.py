import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Включаем логирование, чтобы в панели Render было видно, что происходит
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменных окружения, которые мы настроили на Render
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("Ошибка: Переменная окружения BOT_TOKEN не задана!")

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! 👋\n"
        f"Я твой бот NicuAI, и я успешно запущен на сервере Render через Docker!"
    )

# Обработчик любых других текстовых сообщений (эхо-бот)
@dp.message()
async def echo_message(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

# Главная функция запуска бота
async def main():
    logging.info("Бот NicuAI запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
