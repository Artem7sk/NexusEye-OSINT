import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from bot.handlers import router

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    # Настраиваем логирование, чтобы видеть ошибки в консоли
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nexus_eye.log"), # Сохраняет всё в файл
        logging.StreamHandler()              # Выводит в консоль
    ]
)
    
    
    if not TOKEN:
        exit("Error: BOT_TOKEN not found in .env file")

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Подключаем наши обработчики команд
    dp.include_router(router)

    print("👁 NexusEye OSINT System Online")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System offline.")
