import asyncio
from playwright.async_api import async_playwright
import requests

BOT_TOKEN = '8190673290:AAE7-xcfdZjvhMfguGYvOrmMxqreZ1C0xIc'
CHAT_ID = '1207180714'

ZARA_URL = 'https://www.zara.com/tr/tr/capraz-duz-deri-sandalet-p12600710.html?v1=452729119'

async def check_stock():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(locale="tr-TR")
        page = await context.new_page()
        await page.goto(ZARA_URL)
        await page.wait_for_selector("button.product-add-button__button", timeout=7000)

        button = await page.query_selector("button.product-add-button__button")
        button_text = await button.inner_text()

        stokta_kelimeler = ["Ekle", "Sepete ekle"]

        if any(kelime in button_text for kelime in stokta_kelimeler):
            send_telegram_message(f"🎉 Zara ürünü stokta! Hemen incele:\n{ZARA_URL}")
        else:
            print("Ürün stokta değil.")

        await browser.close()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print(f"Telegram mesaj durumu: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(check_stock())
