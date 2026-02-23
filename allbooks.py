from urllib.parse import urljoin
import os
import json
import requests
from datetime import datetime
from flask import Blueprint, jsonify
from bs4 import BeautifulSoup

bookstoscrapeall_bp = Blueprint('bookstoscrapeall_bp', __name__)

# Filnamn för cache
PROGRAM_CACHE_FILE = "bookstoscrapeall_cache.json"

url = "https://books.toscrape.com/"

# --- ROUTEN ---
@bookstoscrapeall_bp.route('/')
def get_programs():
    # 1. Kolla om filen finns
    if os.path.exists(PROGRAM_CACHE_FILE):
        print("Fil hittad! Läser in från JSON...")
        with open(PROGRAM_CACHE_FILE, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
            # Vi markerar att datan kommer från filen just nu
            full_data["source"] = "local_json_file"
            return jsonify(full_data)

    else:
        # 2. Om filen INTE finns, skrapa
        print(f"Ingen fil hittad. Skrapar {url} live...")
        program_list = scrape_bookstoscrapeall()

        # 3. Skapa strukturen (objektet) som vi vill spara
        full_data = {
            "provider": "BooksToScrape",
            "source": "live_web_scrape",
            "scraped_at": str(datetime.now()),
            "count": len(program_list),
            "program": program_list
        }

        # 4. Spara ner hela objektet till filen
        if program_list:
            with open(PROGRAM_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, ensure_ascii=False, indent=4)

        return jsonify(full_data)


# Skrapar alla böcker på alla sidor
@bookstoscrapeall_bp.route("/")
def scrape_bookstoscrapeall():
    base_url = "https://books.toscrape.com/"

    # Vi börjar på första sidan
    current_url = base_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    all_books = []  # En stor lista för ALLA sidors böcker
    page_count = 1  # Bara för att vi ska se i loggen vad som händer

    # --- STARTA LOOPEN ---
    # Så länge 'current_url' har ett värde, fortsätt köra
    while current_url:
        print(f"Skrapar sida {page_count}: {current_url}...")  # Bra för att se att det inte hängt sig

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. HÄMTA BÖCKERNA PÅ DENNA SIDA (Samma kod som förut)
            book_containers = soup.find_all('article', class_='product_pod')

            for book in book_containers:
                # --- Titel & Länk ---
                h3_tag = book.find('h3')
                title = "Okänd titel"
                full_link = "N/A"

                if h3_tag:
                    link_tag = h3_tag.find('a')
                    if link_tag:
                        if link_tag.get('title'):
                            title = link_tag.get('title')
                        elif link_tag.get_text(strip=True):
                            title = link_tag.get_text(strip=True)

                        relative_link = link_tag.get('href')
                        # Använd urljoin för att bygga länken korrekt oavsett vilken sida vi är på
                        full_link = urljoin(current_url, relative_link)

                # --- Rating ---
                rating_tag = book.find('p', class_='star-rating')
                star_rating = rating_tag['class'][1] if rating_tag else "Unknown"

                # --- Pris ---
                price_tag = book.find('p', class_='price_color')
                price = price_tag.get_text(strip=True) if price_tag else "N/A"

                # Lägg till i stora listan
                all_books.append({
                    "title": title,
                    "rating": star_rating + " Stars",
                    "price": price,
                    "link": full_link
                })

            # 2. LETA EFTER "NEXT"-KNAPPEN
            # I HTML ser den ut så här: <li class="next"><a href="...">next</a></li>
            next_li = soup.find('li', class_='next')

            if next_li:
                next_link_tag = next_li.find('a')
                next_href = next_link_tag.get('href')

                # Det här är magin: urljoin räknar ut den nya URL:en automatiskt
                # Den förstår om den ska lägga till "catalogue/" eller inte.
                current_url = urljoin(current_url, next_href)
                page_count += 1
            else:
                # Ingen "Next"-knapp hittades -> Vi är klara!
                print("Ingen mer 'Next'-knapp. Skrapning klar.")
                current_url = None

        except Exception as e:
            print(f"Ett fel uppstod på sida {page_count}: {e}")
            current_url = None  # Avbryt om det blir fel

    return all_books