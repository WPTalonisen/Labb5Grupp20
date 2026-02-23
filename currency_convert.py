import requests


def get_gbp_to_sek_rate():
    # Vi försökte använda google först men det krånglade bara så vi bytte till denna!
    # Gemini gav oss länken
    url = "https://api.frankfurter.app/latest?from=GBP&to=SEK"

    try:

        response = requests.get(url)
        # Kollar om response är mellan 200-299, om inte så ger den HTTPerror
        response.raise_for_status()
        data = response.json()

        # Plockar ut just SEK från svaret
        rate = data['rates']['SEK']

        print(f"Hittade växelkurs via API: 1 GBP = {rate} SEK")
        return float(rate)

    except Exception as e:
        print(f"Kunde inte hämta valuta: {e}")
        return 14.0  # Fallback om API inte funkar