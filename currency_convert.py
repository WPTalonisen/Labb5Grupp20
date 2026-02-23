import requests


def get_gbp_to_sek_rate():
    # Vi använder ett gratis API istället för att skrapa, mycket mer stabilt!
    url = "https://api.frankfurter.app/latest?from=GBP&to=SEK"

    try:
        # Timeout på 10 sekunder precis som innan
        response = requests.get(url, timeout=10)

        # Om API:et svarar med ett fel (t.ex. 404 eller 500) fångas det här
        response.raise_for_status()

        # Gör om svaret till JSON
        data = response.json()

        # Plockar ut just SEK-kursen från JSON-svaret
        rate = data['rates']['SEK']

        print(f"Hittade växelkurs via API: 1 GBP = {rate} SEK")
        return float(rate)

    except Exception as e:
        print(f"Kunde inte hämta valuta: {e}")
        return 14.0  # Fallback om API inte funkar