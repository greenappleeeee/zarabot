import os
import asyncio
from playwright.async_api import async_playwright
import requests

URL = "https://www.zara.com/tr/tr/capraz-duz-deri-sandalet-p12600710.html?v1=452729119"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    return response

async def check_stock():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(URL, wait_until='networkidle')
        await asyncio.sleep(5)  # Sayfanın tam yüklenmesi için bekle

        # Sayfa içeriğini dosyaya kaydet (inceleme için)
        content = await page.content()
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(content)

        # Stok butonunu arıyoruz (selector'u ihtiyaca göre değiştirebilirsin)
        try:
            await page.wait_for_selector("button:has-text('Sepete ekle')", timeout=15000)
            print("Ürün stokta.")
            send_telegram_message("Ürün stokta!")
        except:
            print("Ürün stokta değil ya da buton bulunamadı.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_stock())

