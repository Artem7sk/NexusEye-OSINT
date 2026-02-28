import re
from aiogram import Router, types
from aiogram.filters import Command
from core.engine import check_nickname

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👁 **NexusEye OSINT System Online**\n\nВведите никнейм для поиска:")

@router.message()
async def handle_search(message: types.Message):
    target = message.text.strip()
    
    # Простая проверка: если есть символ @, ищем почту
    if "@" in target and "." in target:
        status_msg = await message.answer(f"🔎 Проверяю email `{target}` на утечки паролей...")
        leaks = await check_email_leak(target)
        
        if leaks:
            response = f"⚠️ **Найдено в {len(leaks)} утечках!**\n\n"
            response += "Данные с этой почты были найдены в следующих базах:\n"
            for leak in leaks[:10]: # Выведем первые 10 для краткости
                response += f"❌ {leak}\n"
            response += "\n*Рекомендуется сменить пароли!*"
        else:
            response = "✅ Почта не найдена в известных базах утечек."
            
    else:
        # Если не почта, ищем никнейм (твой старый код)
        status_msg = await message.answer(f"🔍 Сканирую сеть по никнейму: `{target}`...")
        found_links = await check_nickname(target)
        
        if found_links:
            response = f"✅ **Найдено совпадений: {len(found_links)}**\n\n"
            for link in found_links:
                response += f"🔹 {link['name']}: {link['url']}\n"
        else:
            response = "❌ Совпадений не найдено."
    
    await status_msg.edit_text(response, disable_web_page_preview=True)
