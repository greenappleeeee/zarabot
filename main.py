import os
import json
import asyncio
from playwright.async_api import async_playwright
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

PRODUCTS_FILE = "products.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def load_products():
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

async def check_stock(product):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(product["url"], wait_until="networkidle")
        await asyncio.sleep(5)

        try:
            # Sayfadaki button, div, span, a etiketlerinin tüm metinlerini al
            texts = await page.locator("button, div, span, a").all_inner_texts()

            # Anahtar kelimelerden herhangi biri metinlerde var mı kontrol et
            found = any(
                any(keyword in t.lower() for keyword in ["sepete ekle", "ekle", "add to cart", "in stock"])
                for t in texts
            )

        except Exception as e:
            print(f"Stok kontrolünde hata: {e}")
            found = False

        if found:
            msg = f"✅ <b>{product['name']}</b> stokta!\n{product['url']}"
        else:
            msg = f"❌ <b>{product['name']}</b> stokta değil.\n{product['url']}"

        print(msg)
        send_telegram_message(msg)

        await browser.close()


ADD_NAME, ADD_URL = range(2)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    count = len(products)
    await update.message.reply_text(f"✅ Bot aktif.\n🔍 Takip edilen ürün sayısı: {count}\n🕐 Stoklar 5 dakikada bir kontrol ediliyor.")

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    if not products:
        await update.message.reply_text("Ürün listesi boş.")
        return
    text = "Takip edilen ürünler:\n"
    for i, p in enumerate(products, 1):
        text += f"{i}. {p['name']}\n"
    await update.message.reply_text(text)

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lütfen eklemek istediğiniz ürünün adını yazın:")
    return ADD_NAME

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_product_name"] = update.message.text
    await update.message.reply_text("Şimdi ürünün tam URL'sini gönderin:")
    return ADD_URL

async def add_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    name = context.user_data.get("new_product_name")
    products = load_products()
    products.append({"name": name, "url": url})
    save_products(products)
    await update.message.reply_text(f"✅ '{name}' ürünü listeye eklendi.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("İşlem iptal edildi.")
    return ConversationHandler.END

async def delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    if not products:
        await update.message.reply_text("Silinecek ürün yok.")
        return
    keyboard = [
        [InlineKeyboardButton(p["name"], callback_data=f"delete_{i}")]
        for i, p in enumerate(products)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Silmek istediğiniz ürünü seçin:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("delete_"):
        index = int(data.split("_")[1])
        products = load_products()
        if 0 <= index < len(products):
            deleted = products.pop(index)
            save_products(products)
            await query.edit_message_text(f"✅ '{deleted['name']}' ürünü listeden silindi.")
        else:
            await query.edit_message_text("Geçersiz seçim.")

async def periodic_check(app):
    while True:
        products = load_products()
        for product in products:
            await check_stock(product)
        await asyncio.sleep(300)  # 5 dakika bekle

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("liste", list_products))

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("ekle", add_start)],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_url)],
        },
        fallbacks=[CommandHandler("iptal", cancel)],
    )
    app.add_handler(add_conv)
    app.add_handler(CommandHandler("durum", status))

    app.add_handler(CommandHandler("sil", delete_start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_repeating(lambda ctx: asyncio.create_task(periodic_check(app)), interval=300, first=10)

    print("Bot çalışıyor...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

