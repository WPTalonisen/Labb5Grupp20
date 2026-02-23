import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask import Blueprint, jsonify, request
from datetime import datetime
from currency_convert import get_gbp_to_sek_rate
import re

# Skapar en blueprint för kategorierna
category_scraper_bp = Blueprint('category_bp', __name__)

BASE_URL = "https://books.toscrape.com/"


def get_category_filename():
    """Skapar ett filnamn med dagens datum."""
    today_date = datetime.now().strftime("%Y-%m-%d")
    return f"categories_{today_date}.json"


def scrape_and_save_categories():
    """Hämtar alla kategorier och deras URL:er, och sparar till en JSON-fil med dagens datum."""
    print("Skrapar kategorier från BooksToScrape...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        category_dict = {}

        # CSS-selektor för att hitta alla a-taggar under den inre ul-listan i sidomenyn
        category_links = soup.select('.side_categories ul ul a')

        for link in category_links:
            # Rensa namnet från mellanslag och radbrytningar
            category_name = link.get_text(strip=True)
            relative_url = link.get('href')

            # Skapa den fullständiga URL:en
            full_url = urljoin(BASE_URL, relative_url)

            category_dict[category_name] = full_url

        # Hämtar dagens filnamn
        filename = get_category_filename()

        # Spara ner till JSON-filen
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(category_dict, f, ensure_ascii=False, indent=4)

        print(f"Sparade {len(category_dict)} kategorier till {filename}")
        return category_dict

    except Exception as e:
        print(f"Ett fel uppstod vid skrapning av kategorier: {e}")
        return None


def get_category_url(category_name):
    """Använder dagens JSON-fil för att hämta URL:en för en specifik kategori."""
    filename = get_category_filename()

    # Skapa filen om den inte redan finns för idag
    if not os.path.exists(filename):
        scrape_and_save_categories()

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            categories = json.load(f)

        # Loopa igenom och gör en sökning som ignorerar stora/små bokstäver
        for key, url in categories.items():
            if key.lower() == category_name.lower().strip():
                return url

        # Om kategorin inte hittades
        return None

    except Exception as e:
        print(f"Kunde inte läsa {filename}: {e}")
        return None


# --- ROUTES FÖR API:ET ---

@category_scraper_bp.route('/', methods=['GET'])
def get_all_categories():
    """Route för att se alla kategorier direkt i webbläsaren/Postman"""
    filename = get_category_filename()

    if not os.path.exists(filename):
        categories = scrape_and_save_categories()
    else:
        with open(filename, 'r', encoding='utf-8') as f:
            categories = json.load(f)

    return jsonify({
        "message": f"Alla kategorier (läser från {filename})",
        "count": len(categories) if categories else 0,
        "categories": categories
    }), 200

def scrape_category_books(start_url, category_name):
    """Skrapar alla böcker från en specifik kategori-URL och hanterar pagination."""
    current_url = start_url
    all_books = []
    page_count = 1

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Hämta valutakursen en gång
    gbp_rate = get_gbp_to_sek_rate()

    while current_url:
        print(f"Skrapar {category_name} - Sida {page_count}...")
        try:
            response = requests.get(current_url, headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            book_containers = soup.find_all('article', class_='product_pod')

            for book in book_containers:
                # Titel & Länk
                h3_tag = book.find('h3')
                title = "Okänd titel"
                full_link = "N/A"

                if h3_tag:
                    link_tag = h3_tag.find('a')
                    if link_tag:
                        title = link_tag.get('title') or link_tag.get_text(strip=True)
                        relative_link = link_tag.get('href')
                        full_link = urljoin(current_url, relative_link)

                # Rating
                rating_tag = book.find('p', class_='star-rating')
                star_rating = rating_tag['class'][1] if rating_tag else "Unknown"

                # Pris i SEK
                price_tag = book.find('p', class_='price_color')
                price_sek = 0
                if price_tag:
                    raw_price = price_tag.get_text(strip=True)
                    clean_price = re.sub(r'[^\d.]', '', raw_price)
                    try:
                        price_sek = round(float(clean_price) * gbp_rate, 2)
                    except ValueError:
                        price_sek = "Error"

                all_books.append({
                    "title": title,
                    "rating": star_rating + " Stars",
                    "price": f"{price_sek} kr",
                    "link": full_link
                })

            # Kolla om det finns en "Next"-knapp i kategorin
            next_li = soup.find('li', class_='next')
            if next_li:
                next_href = next_li.find('a').get('href')
                current_url = urljoin(current_url, next_href)
                page_count += 1
            else:
                current_url = None # Ingen mer sida, avsluta loopen

        except Exception as e:
            print(f"Fel vid skrapning av kategori på sida {page_count}: {e}")
            current_url = None

    return all_books

# Hittar specifik kategori och skrapar den för böcker
@category_scraper_bp.route('/<string:category_name>', methods=['GET'])
def find_specific_category(category_name):
    """Söker efter en kategori, skrapar dess böcker och sparar i en JSON-fil"""

    # 1. Hämta URL för kategorin med din befintliga funktion
    url = get_category_url(category_name)

    if not url:
        return jsonify({"error": f"Kategorin '{category_name}' hittades inte."}), 404

    # 2. Skapa ett snyggt filnamn utan mellanslag och med dagens datum
    safe_category = category_name.lower().replace(" ", "_")
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{safe_category}_{today_date}.json"

    # 3. Cache-koll: Om vi redan har skrapat denna kategori idag, returnera filen direkt
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data["message"] = f"Hämtade {category_name} från dagens cache."
            return jsonify(data), 200

    # 4. Om filen inte finns, kör skrapningen!
    print(f"Ingen cache för {category_name}. Skrapar från {url}...")
    scraped_books = scrape_category_books(url, category_name)

    # 5. Strukturera datan som ska sparas och skickas tillbaka
    data = {
        "message": f"Kategorin '{category_name}' nyskrapad!",
        "category": category_name,
        "source_url": url,
        "scraped_at": str(datetime.now()),
        "count": len(scraped_books),
        "books": scraped_books
    }

    # 6. Spara till den nya JSON-filen
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonify(data), 200