import asyncio
import aiohttp
import re # Используем стандартный модуль регулярных выражений вместо phonenumbers
from fpdf import FPDF
import os
from bs4 import BeautifulSoup


# Список сайтов для проверки (для начала возьмем самые популярные)
SOCIAL_NETWORKS = {
    "Instagram": "https://www.instagram.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "GitHub": "https://github.com/{}",
    "Twitter (X)": "https://twitter.com/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Telegram": "https://t.me/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "VK (ВКонтакте)": "https://vk.com/{}",
    "Odnoklassniki": "https://ok.ru/{}",
    "Habr": "https://habr.com/ru/users/{}",
    "LiveJournal": "https://{}.livejournal.com",
    "Twitch": "https://www.twitch.org/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Medium": "https://medium.com/@{}",
    "DeviantArt": "https://www.deviantart.com/{}",
    "Flickr": "https://www.flickr.com/people/{}",
    "Vimeo": "https://vimeo.com/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Behance": "https://www.behance.net/{}",
    "Dribbble": "https://dribbble.com/{}",
    "Pikabu": "https://pikabu.ru/@{}",
    "VC.ru": "https://vc.ru/u/{}",
    "Livelib": "https://www.livelib.ru/reader/{}",
    "Chess.com": "https://www.chess.com/member/{}",
    "Duolingo": "https://www.duolingo.com/profile/{}",
    "Roblox": "https://www.roblox.com/user.aspx?username={}"
}


async def check_nickname(nickname: str):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, url in SOCIAL_NETWORKS.items():
            target_url = url.format(nickname)
            tasks.append(fetch(session, name, target_url))
        
        results = await asyncio.gather(*tasks)
    return [res for res in results if res]

async def fetch(session, name, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        async with session.get(url, headers=headers, timeout=5, allow_redirects=True) as response:
            # На некоторых сайтах 200 бывает даже если профиля нет, 
            # но для большинства этот метод работает.
            if response.status == 200 and url.split('/')[-1].lower() in (await response.text()).lower():
                return {"name": name, "url": url}
    except:
        pass
    return None


async def check_email_leak(email: str):
    # Используем проверенный публичный API
    url = f"https://leakcheck.io/api/public?check={email}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # Если успех и есть список источников
                    if data.get("success") and data.get("sources"):
                        # Возвращаем список названий баз данных
                        return [source["name"] for source in data["sources"]]
        except Exception as e:
            print(f"Ошибка в модуле Email: {e}")
    return None

async def check_phone(phone_number: str):
    # Очищаем только цифры
    clean_phone = "".join(filter(str.isdigit, phone_number))
    
    # Справочник префиксов (Казахстан и РФ)
    prefixes = {
        # Казахстан
        "7701": ("Kcell/activ", "Казахстан"),
        "7702": ("Kcell/activ", "Казахстан"),
        "7705": ("Beeline", "Казахстан"),
        "7777": ("Beeline", "Казахстан"),
        "7707": ("Tele2", "Казахстан"),
        "7747": ("Tele2", "Казахстан"),
        "7700": ("Altel", "Казахстан"),
        "7708": ("Altel", "Казахстан"),
        # РФ (основные)
        "7903": ("Beeline", "Россия"),
        "7909": ("Beeline", "Россия"),
        "7910": ("МТС", "Россия"),
        "7916": ("МТС", "Россия"),
        "7925": ("МегаФон", "Россия"),
        "7926": ("МегаФон", "Россия"),
        "7999": ("Yota (Виртуальный)", "Россия"),
    }

    # Ищем совпадение по первым 4 цифрам
    prefix = clean_phone[:4]
    operator, region = prefixes.get(prefix, ("Неизвестный оператор", "Регион не определен"))

    # Если это городской номер Казахстана (например, +7727 - Алматы)
    if clean_phone.startswith("7727"):
        operator, region = "Городской номер", "Алматы, Казахстан"
    elif clean_phone.startswith("7717"):
        operator, region = "Городской номер", "Астана, Казахстан"

    return {
        "region": region,
        "operator": operator,
        "format_intl": f"+{clean_phone}",
        "whatsapp": f"https://wa.me/{clean_phone}",
        "telegram": f"https://t.me/+{clean_phone}"
    }

async def generate_pdf_report(user_id, target, results):
    pdf = FPDF()
    pdf.add_page()
    
    # Заголовок
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"OSINT Report: {target}", ln=True, align='C')
    pdf.ln(10)
    
    # Данные
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated for User ID: {user_id}", ln=True)
    pdf.cell(0, 10, f"Status: Investigated", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Found Resources:", ln=True)
    pdf.set_font("Arial", "", 11)
    
    # Перечисляем найденные ссылки
    for res in results:
        pdf.cell(0, 10, f"- {res['name']}: {res['url']}", ln=True)
    
    # Сохраняем файл
    file_path = f"reports/report_{user_id}_{target}.pdf"
    pdf.output(file_path)
    return file_path

async def check_car_number(car_number: str):
    # Очищаем номер от пробелов и приводим к верхнему регистру
    clean_number = re.sub(r'[^A-Z0-9А-Я]', '', car_number.upper())
    
    # Базовая проверка формата (пример для РФ/РК: 777AAA01 или А111АА77)
    if len(clean_number) < 4:
        return None

    # Формируем ссылки на самые популярные агрегаторы (бесплатные)
    # Для РФ: Номерограм (отлично находит фото авто)
    # Для РК: Сервисы проверки страховки/техосмотра
    
    info = {
        "number": clean_number,
        "links": [
            {"name": "📸 Номерограм (Фото и история)", "url": f"https://www.nomerogram.ru/s/{clean_number}/"},
            {"name": "🚗 Автокод (История владения)", "url": f"https://avtocod.ru/proverka-avto-po-gos-nomeru?cd={clean_number}"},
            {"name": "📝 Проверка ОСАГО/Страховки", "url": f"https://autoins.ru/osago/proverka-polisa-osago/"}
        ]
    }
    
    # Здесь можно добавить реальный парсинг через aiohttp, 
    # если найдем открытый эндпоинт без капчи.
    return info
async def check_fraud_and_ads(target: str):
    """
    Ищет упоминания цели на OLX/Avito и в черных списках через поисковые индексы.
    """
    # Список площадок для поиска объявлений и жалоб
    platforms = {
        "OLX": f"https://www.google.com/search?q=site:olx.kz+%22{target}%22",
        "Avito": f"https://www.google.com/search?q=site:avito.ru+%22{target}%22",
        "Scam Search": f"https://www.google.com/search?q=%22{target}%22+мошенник+скам+кидала",
        "ТНД (Казахстан)": f"https://www.google.com/search?q=site:tnd.kz+%22{target}%22"
    }
    
    found_info = []
    for name, url in platforms.items():
        found_info.append({"name": name, "url": url})
        
    return found_info

async def get_scam_status(phone_number: str):
    clean_phone = "".join(filter(str.isdigit, phone_number))
    
    # Списки подозрительных префиксов (примеры виртуальных и VOIP номеров)
    # РФ: 999, 958, 939 и т.д.
    # РК: некоторые диапазоны виртуальных операторов
    suspicious_prefixes = ['7999', '7958', '7939', '7700', '7771'] 
    
    is_virtual = any(clean_phone.startswith(pre) for pre in suspicious_prefixes)
    
    if is_virtual:
        return "⚠️ **Внимание:** Используется виртуальный или временный номер. Возможен риск мошенничества!"
    
    if len(clean_phone) < 11:
        return "❓ Номер слишком короткий для полной проверки."
        
    return "✅ Прямых угроз не обнаружено (база РФ/РК)"

