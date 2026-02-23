from flask import Flask
from duprograms import duprograms_bp
from timeedit import timeedit_bp
from bookstoscrape import bookstoscrape_bp
from bookscrapeall import bookstoscrapeall_bp
from ui import ui_bp

app = Flask(__name__)
app.json.sort_keys = False # Sorterar inte JSON filer efter bokstavsordning

# Registrerar blueprinten
app.register_blueprint(duprograms_bp, url_prefix="/duprograms")
app.register_blueprint(timeedit_bp, url_prefix="/timeedit")
app.register_blueprint(bookstoscrape_bp, url_prefix="/bookstoscrape")
app.register_blueprint(bookstoscrapeall_bp, url_prefix="/bookstoscrapeall")
app.register_blueprint(ui_bp, url_prefix="/ui")

if __name__ == "__main__":
    app.run(debug=True)