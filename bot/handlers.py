from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👁 **NexusEye OSINT System Online**\n\n"
        "Отправьте мне никнейм, почту или телефон для начала поиска.\n"
        "Доступные модули: Sherlock, BreachCheck, GeoIP."
    )

@router.message()
async def handle_search(message: types.Message):
    # Здесь будет логика вызова функций из core/engine.py
    await message.answer(f"🔍 Начинаю поиск по запросу: {message.text}...")
