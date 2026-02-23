import requests
from bs4 import BeautifulSoup

# Skrapar Googles valute converter
def get_gbp_to_sek_rate():
    url = "https://www.google.com/finance/quote/GBP-SEK"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Google Finance brukar ha klassen "YMlKec fxKbKc" för den stora valutasiffran
        # Taget från Gemini
        rate_element = soup.find('div', class_='YMlKec fxKbKc')

        if rate_element:
            # Hämta texten, och se till att det blir en float, byt komma mot punkt om det behövs
            rate_text = rate_element.get_text(strip=True).replace(',', '.')
            print(f"Hittade växelkurs: {rate_text}")
            return float(rate_text)
        else:
            print("Kunde inte hitta elementet för växelkursen.")
            return 14.0  # Om scraping misslyckas (ungefärlig kurs)

    except Exception as e:
        print(f"Kunde inte hämta valuta: {e}")
        return 14.0  # Fallback