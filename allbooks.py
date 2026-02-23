from urllib.parse import urljoin
import os
import json
import requests
import re  # <--- NY: Behövs för att rensa priset snyggt
from datetime import datetime
from flask import Blueprint, jsonify
from bs4 import BeautifulSoup
from currency_convert import get_gbp_to_sek_rate

bookstoscrapeall_bp = Blueprint('bookstoscrapeall_bp', __name__)

PROGRAM_CACHE_FILE = "bookstoscrapeall_cache.json"


@bookstoscrapeall_bp.route('/')
def get_programs():
    if os.path.exists(PROGRAM_CACHE_FILE):
        print("Fil hittad! Läser in från JSON...")
        with open(PROGRAM_CACHE_FILE, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
            full_data["source"] = "local_json_file"
            return jsonify(full_data)
    else:
        print(f"Ingen fil hittad. Skrapar live...")
        program_list = scrape_bookstoscrapeall()

        full_data = {
            "provider": "BooksToScrape",
            "source": "live_web_scrape",
            "scraped_at": str(datetime.now()),
            "count": len(program_list),
            "program": program_list
        }

        if program_list:
            with open(PROGRAM_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, ensure_ascii=False, indent=4)

        return jsonify(full_data)


@bookstoscrapeall_bp.route("/")
def scrape_bookstoscrapeall():
    base_url = "https://books.toscrape.com/"
    current_url = base_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    all_books = []
    page_count = 1

    # HÄMTA VALUTAKURSEN INNAN LOOPEN
    # Vi vill inte hämta kursen 50 gånger (en gång per sida), det tar för lång tid.
    gbp_rate = get_gbp_to_sek_rate()
    print(f"Använder växelkurs: 1 GBP = {gbp_rate} SEK")

    while current_url:
        print(f"Skrapar sida {page_count}: {current_url}...")

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            # Tvinga encoding till utf-8 för att slippa "Â£" problem
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
                        if link_tag.get('title'):
                            title = link_tag.get('title')
                        elif link_tag.get_text(strip=True):
                            title = link_tag.get_text(strip=True)

                        relative_link = link_tag.get('href')
                        full_link = urljoin(current_url, relative_link)

                # Rating
                rating_tag = book.find('p', class_='star-rating')
                star_rating = rating_tag['class'][1] if rating_tag else "Unknown"

                # Pris & Valutaomvandling
                price_tag = book.find('p', class_='price_color')
                price_str = "N/A"
                price_sek = 0

                if price_tag:
                    raw_price = price_tag.get_text(strip=True)  # T.ex "£51.77"

                    # Rensa strängen: Ta bort allt som INTE är siffror eller punkt
                    # Detta tar bort '£', 'Â' och andra tecken.
                    clean_price = re.sub(r'[^\d.]', '', raw_price)

                    try:
                        # 2. Gör om till float
                        price_float = float(clean_price)

                        # 3. Räkna ut SEK
                        price_sek = round(price_float * gbp_rate, 2)

                        # Spara originalsträngen (GBP)
                        price_str = raw_price
                    except ValueError:
                        price_str = raw_price
                        price_sek = "Error"

                # Lägg till i stora listan
                all_books.append({
                    "title": title,
                    "rating": star_rating + " Stars",
                    "price_gbp": price_str,  # Originalpriset i GBP
                    "price_sek": f"{price_sek} kr",  # Det nya priset i SEK
                    "link": full_link
                })

            # --- Next Button Logic ---
            next_li = soup.find('li', class_='next')
            if next_li:
                next_link_tag = next_li.find('a')
                next_href = next_link_tag.get('href')
                current_url = urljoin(current_url, next_href)
                page_count += 1
            else:
                print("Ingen mer 'Next'-knapp. Skrapning klar.")
                current_url = None

        except Exception as e:
            print(f"Ett fel uppstod på sida {page_count}: {e}")
            current_url = None

    return all_books