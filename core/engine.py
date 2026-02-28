import asyncio
import aiohttp

# Список сайтов для проверки (для начала возьмем самые популярные)
SOCIAL_NETWORKS = {
    "Instagram": "https://www.instagram.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "GitHub": "https://github.com/{}",
    "Twitter (X)": "https://twitter.com/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Telegram": "https://t.me/{}",
    "Pinterest": "https://www.pinterest.com/{}/"
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
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                return {"name": name, "url": url}
    except:
        pass
    return None

async def check_email_leak(email: str):
    # Используем открытое API для проверки утечек (например, leakcheck.io или аналоги)
    # Для примера возьмем простой запрос к публичному источнику
    url = f"https://api.leakcheck.net/public?check={email}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("sources"):
                        return data.get("sources") # Возвращает список названий утечек
        except Exception as e:
            print(f"Ошибка поиска почты: {e}")
    return None  
