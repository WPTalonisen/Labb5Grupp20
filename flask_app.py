from flask import Flask, jsonify
from blueprint.scraper import bookstoscrapeall_bp
from blueprint.crud import book_crud_bp
from blueprint.homepage import homepage_bp

app = Flask(__name__)
app.json.sort_keys = False # Sorterar inte JSON filer efter bokstavsordning

# Registrerar blueprinten
app.register_blueprint(bookstoscrapeall_bp, url_prefix="/bookstoscrapeall")
app.register_blueprint(book_crud_bp, url_prefix="/bookstoscrapeall")
app.register_blueprint(homepage_bp, url_prefix="/")

if __name__ == "__main__":
    app.run(debug=True)