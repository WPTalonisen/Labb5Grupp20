from flask import Flask
from program import bookstoscrape_bp
from allbooks import bookstoscrapeall_bp

app = Flask(__name__)
app.json.sort_keys = False # Sorterar inte JSON filer efter bokstavsordning

# Registrerar blueprinten
app.register_blueprint(bookstoscrape_bp, url_prefix="/bookstoscrape")
app.register_blueprint(bookstoscrapeall_bp, url_prefix="/bookstoscrapeall")


if __name__ == "__main__":
    app.run(debug=True)