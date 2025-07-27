<<<<<<< HEAD
import json
import os

PRODUCTS_FILE = "products.json"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

def add_url(url, name):
    products = load_products()
    if any(p["url"] == url for p in products):
        return False  # zaten var
    products.append({"url": url, "name": name, "notified": False})
    save_products(products)
    return True

def remove_url(url):
    products = load_products()
    new_products = [p for p in products if p["url"] != url]
    if len(new_products) == len(products):
        return False  # silinecek url yok
    save_products(new_products)
    return True

def list_urls():
    return load_products()
=======
import json
import os

PRODUCTS_FILE = "products.json"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

def add_url(url, name):
    products = load_products()
    if any(p["url"] == url for p in products):
        return False  # zaten var
    products.append({"url": url, "name": name, "notified": False})
    save_products(products)
    return True

def remove_url(url):
    products = load_products()
    new_products = [p for p in products if p["url"] != url]
    if len(new_products) == len(products):
        return False  # silinecek url yok
    save_products(new_products)
    return True

def list_urls():
    return load_products()
>>>>>>> df712be8ea6fcce895b11e2adae2ac419e9f84af
