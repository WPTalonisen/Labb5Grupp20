from flask import Flask, jsonify
from blueprint.scraper import bookstoscrapeall_bp
from blueprint.crud import book_crud_bp
from blueprint.homepage import homepage_bp
from blueprint.categoryscraper import category_scraper_bp
from blueprint.categorycrud import category_crud_bp

app = Flask(__name__)
app.json.sort_keys = False # Sorterar inte JSON filer efter bokstavsordning

# Registrerar blueprinten

# Den här finns för att Wille gjorde fel och lade allt för mycket tid på den för att låta den tas bort
app.register_blueprint(bookstoscrapeall_bp, url_prefix="/bookstoscrapeall")
app.register_blueprint(book_crud_bp, url_prefix="/books")
app.register_blueprint(homepage_bp, url_prefix="/")
app.register_blueprint(category_scraper_bp, url_prefix="/categories")
app.register_blueprint(category_crud_bp, url_prefix="/categories")

if __name__ == "__main__":
    app.run(debug=True)