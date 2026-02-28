from aiogram import Router, types
from aiogram.filters import Command
from core.engine import check_nickname

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👁 **NexusEye OSINT System Online**\n\nВведите никнейм для поиска:")

@router.message()
async def handle_search(message: types.Message):
    nickname = message.text.strip()
    
    # Чтобы пользователь не скучал, пока идет поиск
    status_msg = await message.answer(f"🔍 Сканирую сеть на наличие никнейма: `{nickname}`...")
    
    found_links = await check_nickname(nickname)
    
    if found_links:
        response = f"✅ **Найдено совпадений: {len(found_links)}**\n\n"
        for link in found_links:
            response += f"🔹 {link['name']}: {link['url']}\n"
    else:
        response = "❌ Совпадений не найдено."
    
    await status_msg.edit_text(response, disable_web_page_preview=True)
