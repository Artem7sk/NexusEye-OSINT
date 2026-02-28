import os
import os
import re
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# ИМПОРТЫ ИЗ ТВОИХ ФАЙЛОВ (CORE)
from core.db import (
    add_user, get_stats, update_request_count, 
    is_user_premium, set_premium_status, get_detailed_stats
)
from core.engine import (
    check_nickname, 
    check_email_leak, 
    generate_pdf_report, 
    check_phone, 
    check_car_number,
    get_scam_status,      # <--- ТЕПЕРЬ БУДЕТ ВИДЕТЬ ЭТО
    check_fraud_and_ads   # <--- И ЭТО
)

def get_main_menu():
    kb = [
        [KeyboardButton(text="🔍 Как пользоваться?"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="💎 Купить Premium"), KeyboardButton(text="📱 Мой ID")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Загружаем переменные окружения
load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

router = Router()

@router.message(F.photo)
async def handle_photo(message: types.Message):
    # 1. Берем самое качественное фото (последнее в списке)
    photo = message.photo[-1]
    file_id = photo.file_id
    
    # 2. Получаем путь к файлу на серверах Telegram
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    
    # 3. Достаем токен прямо из бота
    token = message.bot.token
    
    status_msg = await message.answer("📸 Фото получено. Подготавливаю ссылки для обратного поиска...")

    # 4. Формируем кнопки с прямыми ссылками
    builder = InlineKeyboardBuilder()
    
    # Формируем базовый URL файла для поисковиков
    img_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    
    builder.row(types.InlineKeyboardButton(
        text="🔍 Найти в Google Lens", 
        url=f"https://www.google.com/searchbyimage?image_url={img_url}")
    )
    builder.row(types.InlineKeyboardButton(
        text="🖼 Найти в Яндекс.Картинках", 
        url=f"https://yandex.ru/images/search?rpt=imageview&url={img_url}")
    )
    builder.row(types.InlineKeyboardButton(
        text="🌐 Поиск в Bing Visual Search", 
        url=f"https://www.bing.com/images/searchbyimage?cbir=sbi&imgurl={img_url}")
    )

    await status_msg.edit_text(
        "✅ **Инструменты поиска по фото готовы!**\n\n"
        "Выберите поисковую систему для анализа лиц, локаций или предметов с этого фото:",
        reply_markup=builder.as_markup()
    )

@router.message(Command("buy"))
async def cmd_buy(message: types.Message):
    await message.answer_invoice(
        title="NexusEye Premium 💎",
        description="Полный доступ к базе утечек, поиск по Email и поддержка проекта.",
        payload="premium_access",
        provider_token="", # Для цифровых товаров (Stars) оставляем ПУСТЫМ
        currency="XTR",    # Код валюты Telegram Stars
        prices=[LabeledPrice(label="Premium", amount=100)], # Цена в Звездах (например, 100)
        start_parameter="premium-buy"
    )

# 2. Обязательное подтверждение ПЕРЕД оплатой (нужно ответить в течение 10 сек)
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

# 3. Финальный шаг: когда оплата прошла успешно
@router.message(F.successful_payment)
async def success_payment(message: types.Message):
    set_premium_status(message.from_user.id, True)
    
    # Уведомление юзеру
    await message.answer("🎉 **Оплата прошла успешно!**\nТеперь вам доступны полные отчеты.")
    
    # УВЕДОМЛЕНИЕ АДМИНУ (ТЕБЕ)
    try:
        admin_text = (
            "💰 **НОВАЯ ПРОДАЖА!**\n"
            f"👤 Юзер: @{message.from_user.username} (ID: `{message.from_user.id}`)\n"
            f"💵 Сумма: 100⭐️ (Telegram Stars)"
        )
        await message.bot.send_message(ADMIN_ID, admin_text)
    except:
        pass

@router.message(Command("vip"))
async def cmd_vip(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        set_premium_status(message.from_user.id, True)
        await message.answer("💎 **Режим разработчика активирован!**\nТеперь вам доступны полные отчеты без ограничений.")
    else:
        await message.answer("❌ Эта команда доступна только владельцу системы.")

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users_count, total_reqs, premium_count = get_detailed_stats()
        
        # Защита от пустых значений
        total_reqs = total_reqs if total_reqs else 0
        premium_count = premium_count if premium_count else 0
        
        # Примерный расчет дохода (если 1 преимум = 100 звезд)
        estimated_stars = premium_count * 100
        
        await message.answer(
            "📊 **NexusEye Business Stats**\n\n"
            f"👤 Юзеров: `{users_count}`\n"
            f"🔎 Поисков: `{total_reqs}`\n"
            "─── Продажи ───\n"
            f"💎 Premium-аккаунтов: `{premium_count}`\n"
            f"⭐️ Заработано (всего): `{estimated_stars}`\n\n"
            f"🚀 Система: `Online`"
        )
    else:
        await message.answer("❌ Доступ закрыт.")


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Добавляем в базу
    add_user(message.from_user.id, message.from_user.username)
    
    welcome_text = (
        "👁 **NexusEye OSINT System v2.0**\n"
        "────────────────────────\n"
        "Система глубокого анализа цифрового следа активирована. "
        "Я помогу вам найти информацию и защититься от мошенников.\n\n"
        
        "🔎 **Что я умею:**\n"
        "├ 👤 **Никнейм:** Поиск аккаунтов в 25+ соцсетях\n"
        "├ 📧 **Email:** Проверка утечек паролей и баз данных\n"
        "├ 📱 **Телефон:** Регион, мессенджеры и история объявлений\n"
        "├ 📸 **Фото:** Поиск людей и объектов по изображениям\n"
        "├ 🚘 **Авто:** История владения и фото по госномеру\n"
        "└ 🛡 **Анти-Фрод:** Проверка на скам, OLX и Avito\n\n"
        
        "📥 **Просто отправьте любой запрос в чат:**\n"
        "Например: `+7705...`, `pavel_durov`, `A777AA01` или фото.\n\n"
        "💎 *Используйте меню ниже для навигации:* "
    )
    
    # Отправляем с нашей Reply-клавиатурой (главное меню)
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")


@router.message(F.text == "🔍 Как пользоваться?")
async def help_menu(message: types.Message):
    text = (
        "📖 **Инструкция NexusEye:**\n\n"
        "1. **Никнейм:** Ищет аккаунты в 25+ соцсетях.\n"
        "2. **Почта:** Проверяет наличие паролей в базах утечек.\n"
        "3. **Телефон:** Определяет регион и дает ссылки на мессенджеры.\n"
        "4. **Фото:** Просто скиньте фото и выберите поисковик.\n\n"
        "💡 *Совет: Для полных отчетов по Email нужен Premium.*"
    )
    await message.answer(text)

@router.message(F.text == "📊 Статистика")
async def user_stats(message: types.Message):
    # Используем твою функцию из db.py
    users_count, total_reqs, _ = get_detailed_stats()
    await message.answer(f"📈 **Общая статистика системы:**\n\n👤 Юзеров: `{users_count}`\n🔎 Всего поисков: `{total_reqs}`")

@router.message(F.text == "💎 Купить Premium")
async def buy_btn(message: types.Message):
    await cmd_buy(message) # Вызываем твою готовую функцию оплаты

@router.message(F.text == "📱 Мой ID")
async def my_id(message: types.Message):
    premium = "Активирован 💎" if is_user_premium(message.from_user.id) else "Обычный 👤"
    await message.answer(f"Твой Telegram ID: `{message.from_user.id}`\nСтатус: **{premium}**")


@router.message()
async def handle_search(message: types.Message):
    target = message.text.strip()
    user_id = message.from_user.id
    
    # 1. Фиксируем запрос и проверяем статус
    update_request_count(user_id)
    premium = is_user_premium(user_id)
    # --- МОДУЛЬ 4: ПОИСК ПО НОМЕРУ АВТО ---
    # Регулярка ловит форматы типа A777AA77 или 777AAA01
    car_pattern = r'^[A-ZА-Я0-9]{4,9}$' 
    if re.match(car_pattern, target) and not target.startswith('+'):
        status_msg = await message.answer(f"🚘 Проверяю автомобиль `{target}`...")
        car_info = await check_car_number(target)
        
        if car_info:
            response = (
                f"🚘 **Анализ транспортного средства:** `{car_info['number']}`\n\n"
                "Система ищет упоминания в базах страховых, аукционах и соцсетях.\n"
                "Ниже представлены ссылки на найденные совпадения и фото:"
            )
            builder = InlineKeyboardBuilder()
            for link in car_info['links']:
                builder.row(types.InlineKeyboardButton(text=link['name'], url=link['url']))
            
            await status_msg.edit_text(response, reply_markup=builder.as_markup())
            return

    # --- МОДУЛЬ 1: ПОИСК ПО НОМЕРУ ТЕЛЕФОНА ---
    if target.startswith('+') or (target.isdigit() and len(target) > 10):
        status_msg = await message.answer(f"📱 Анализирую номер `{target}`...")
        
        phone_info = await check_phone(target)
        scam_status = await get_scam_status(target) # Наша новая проверка
        ads_links = await check_fraud_and_ads(target)
        
        if phone_info:
            # Формируем красивый ответ
            response = (
                f"📱 **Анализ номера:** `{target}`\n"
                f"────────────────────────\n"
                f"🛡 **Безопасность:** {scam_status}\n\n"
                f"🌍 **Регион:** `{phone_info['region']}`\n"
                f"📡 **Оператор:** `{phone_info['operator']}`\n"
                f"🔢 **Формат:** `{phone_info['format_intl']}`\n"
                f"────────────────────────\n"
                f"📦 **Следы в сети и объявления:**\n"
                f"Проверьте историю продаж и возможные жалобы по кнопкам ниже:"
            )

            
            builder = InlineKeyboardBuilder()
            # Кнопки мессенджеров
            builder.row(
                types.InlineKeyboardButton(text="WhatsApp", url=phone_info['whatsapp']),
                types.InlineKeyboardButton(text="Telegram", url=phone_info['telegram'])
            )
            # Кнопки OLX/Avito/Scam
            for link in ads_links:
                builder.row(types.InlineKeyboardButton(text=f"🔍 {link['name']}", url=link['url']))
                
            await status_msg.edit_text(response, reply_markup=builder.as_markup(), disable_web_page_preview=True)
            return


    # --- МОДУЛЬ 2: ПОИСК ПО EMAIL ---
    elif "@" in target and "." in target:
        status_msg = await message.answer(f"🔎 Проверяю email `{target}` на утечки...")
        leaks = await check_email_leak(target)
        
        builder = InlineKeyboardBuilder()
        
        if leaks:
            response = f"⚠️ **Найдено в {len(leaks)} утечках!**\n\n"
            
            if not premium and len(leaks) > 2:
                for leak in leaks[:2]:
                    response += f"❌ {leak}\n"
                response += f"\n...и еще **{len(leaks) - 2}** баз данных скрыто.\n"
                response += "\n💎 *Разблокируйте полный отчет прямо сейчас!*"
                
                builder.row(types.InlineKeyboardButton(
                    text="🔓 Открыть весь список (100 ⭐️)", 
                    callback_data="start_buy")
                )
            else:
                for leak in leaks:
                    response += f"❌ {leak}\n"
                response += "\n✅ Полный отчет сформирован."
        else:
            response = "✅ Почта не найдена в известных базах утечек."
            
        await status_msg.edit_text(response, reply_markup=builder.as_markup(), disable_web_page_preview=True)
            
    # --- МОДУЛЬ 3: ПОИСК ПО НИКНЕЙМУ ---
    else:
        status_msg = await message.answer(f"🔍 Сканирую сеть: `{target}`...")
        found_links = await check_nickname(target)
        
        # Создаем билдер для кнопки PDF
        builder = InlineKeyboardBuilder()
        
        if found_links:
            response = f"✅ **Найдено совпадений: {len(found_links)}**\n\n"
            for link in found_links[:15]:
                response += f"🔹 {link['name']}: {link['url']}\n"
            
            # Добавляем кнопку скачивания PDF
            builder.row(types.InlineKeyboardButton(
                text="📂 Скачать полный PDF-отчет", 
                callback_data=f"pdf_{target}")
            )
            # ВАЖНО: Добавляем reply_markup здесь!
            await status_msg.edit_text(response, reply_markup=builder.as_markup(), disable_web_page_preview=True)
        else:
            response = "❌ Совпадений не найдено."
            await status_msg.edit_text(response, disable_web_page_preview=True)

# --- ОБРАБОТЧИКИ КНОПОК ---

# 1. Обработка кнопки PDF
@router.callback_query(F.data.startswith("pdf_"))
async def send_pdf_report_call(callback: types.CallbackQuery):
    target = callback.data.replace("pdf_", "")
    user_id = callback.from_user.id
    
    # Снова получаем ссылки для отчета
    found_links = await check_nickname(target)
    
    if found_links:
        await callback.answer("Генерирую отчет...")
        file_path = await generate_pdf_report(user_id, target, found_links)
        
        document = FSInputFile(file_path)
        await callback.message.answer_document(document, caption=f"📄 Полный отчет по цели: {target}")
        
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)
    else:
        await callback.answer("Ошибка: данные не найдены.", show_alert=True)

# 2. Обработка кнопки покупки (Stars)
@router.callback_query(F.data == "start_buy")
async def process_buy_callback(callback: types.CallbackQuery):
    await cmd_buy(callback.message)
    await callback.answer()
