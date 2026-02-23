import os
import json
import requests
from datetime import datetime
from flask import Blueprint, jsonify
from bs4 import BeautifulSoup

# Skapa Blueprint
bookstoscrape_bp = Blueprint('bookstoscrape_bp', __name__)

# Filnamn för cache
PROGRAM_CACHE_FILE = "bookstoscrape_cache.json"

url = "https://books.toscrape.com/"

# --- ROUUTEN ---
@bookstoscrape_bp.route('/')
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
        program_list = scrape_bookstoscrape()

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


# --- SKRAPNINGSFUNKTIONEN ---
def scrape_bookstoscrape():

    base_url = "https://books.toscrape.com/"

    # Webbsidor brukar blocka scripts automatiskt, User-Agent lurar hemsidan och får scriptet att se ut som en vanlig användare
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    programs = []

    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Hitta alla divar med rätt klass
        book_containers = soup.find_all('article', class_='product_pod')

        for book in book_containers:
            title = ""
            h3_tag = book.find('h3')
            link_tag = book.find('a')



            # Detta är en säkerhetsspärr.
            #
            # Innan vi försöker läsa något från link_tag, måste vi veta att vi faktiskt hittade en länk.
            #
            # Om link_tag är None (tomt) och vi försöker köra .get(), kraschar hela programmet.
            if link_tag:


                # Här letar vi efter attributet title="..." inuti taggen.
                #
                #     Varför först? Det här är "Guldstandarden". Den innehåller oftast den fullständiga, oförstörda datan.
                #
                #     Om den hittas → Vi sparar den i variabeln title.
                #
                #     Om den är tom (eller inte finns) → Vi hoppar vidare till elif.
                if link_tag.get('title'):
                    title = link_tag.get('title')



                    # Den här raden körs bara om Plan A misslyckades.
                    #
                    #     .get_text(): Hämtar den synliga texten mellan <a> och </a>.
                    #
                    #     strip=True: Detta är en städare. Den tar bort onödiga mellanslag och radbrytningar före och efter texten.
                    #
                    #         Utan strip: "   Harry Potter   \n"
                    #
                    #         Med strip: "Harry Potter"
                elif link_tag.get_text(strip=True):
                    title = link_tag.get_text(strip=True)


            # Vi kollar: "Är variabeln title fortfarande tom?"
            #
            # Om vi redan hittade en titel i förra steget (Plan A eller B), hoppar koden över hela det här blocket. Vi vill inte göra onödigt jobb.
            #
            # Om title är tom, går vi in i blocket.
            if title == "":

                # Vi letar efter en <img>-tagg inuti bok-containern (book).
                #
                #     Vi bryr oss inte om vilken bild det är just nu, vi tar den första vi hittar (vilket oftast är omslaget).
                img_tag = book.find('img')

                # Här gör vi två kontroller i en smäll:
                #
                #     if img_tag: "Hittade vi ens en bild?" (Om img_tag är None får vi inte fortsätta, annars kraschar koden).
                #
                #     and img_tag.get('alt'): "Har den här bilden en alt-text?" (Vissa dekorativa bilder saknar text)
                if img_tag and img_tag.get('alt'):

                    # Nu stjäl vi texten från bilden och sparar den som vår titel.
                    #
                    #     Vi tar värdet från alt="...".
                    #
                    #     Nu har vi räddat situationen och fått en titel, trots att textlänken var trasig eller tom.
                    title = img_tag.get('alt')

            relative_link = link_tag.get('href')
            rating_tag = book.find('p', class_='star-rating')

            if rating_tag:
                star_rating = rating_tag['class'][1]
            else:
                star_rating = "Unknown"

            price_tag = book.find('p', class_='price_color')
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            full_link = f"{base_url}{relative_link}"

            programs.append({
                "title": title,
                "rating": star_rating + " Stars",
                "price": price,
                "link": full_link
            })

    except Exception as e:
        print(f"Ett fel uppstod vid skrapning: {e}")

    return programs