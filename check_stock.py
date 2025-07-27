import asyncio
import json
from playwright.async_api import async_playwright

async def check_stock(product):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto(product["url"], timeout=60000)

                btn = await page.query_selector("button:has-text('Sepete Ekle')")
                if btn:
                    text = (await btn.inner_text()).strip().lower()
                    keywords = ["sepete ekle", "ekle", "add to cart", "in stock"]
                    if any(keyword in text for keyword in keywords):
                        return True

                return False
            finally:
                await browser.close()
    except Exception as e:
        print("Stok kontrol hatası:", e)
        return False


async def periodic_check(chat_id, bot):
    try:
        with open("products.json", "r", encoding="utf-8") as f:
            products = json.load(f)
    except FileNotFoundError:
        products = []

    for product in products:
        in_stock = await check_stock(product)
        if in_stock and not product.get("notified", False):
            product["notified"] = True
            message = f"STOKTA: {product['name']}\n{product['url']}"
            await bot.send_message(chat_id=chat_id, text=message)
        elif not in_stock:
            product["notified"] = False

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
