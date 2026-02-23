from flask import Blueprint, request, jsonify



homepage_bp = Blueprint('homepage_bp', __name__)

@homepage_bp.route('/')
def api_tutorial():
    return jsonify({
        "message": "Välkommen till Grupp 20's REST API. Här nedan så kan du se vad du kan göra och vart! Låtsas att detta är en fin hemsida med tusentals CSS rader.",
        "användning": {
            "GET get_all_categories": {
                "method": "GET",
                "url": "/categories",
                "description": "Hämtar alla kategorier från dagens cache eller skrapar nytt."
            },
            "GET find_specific_category": {
                "method": "GET",
                "url": "/catgegories/(kategori)",
                "description": "Hämtar specifik kategori från user input och skrapar den sidan, lagrar sedan alla böcker i separat fil."
            },
            "GET all_books": {
                "method": "GET",
                "url": "/bookstoscrapeall/",
                "description": "Hämtar alla böcker från dagens cache eller skrapar nytt."
            },
            "GET find_book": {
                "method": "GET",
                "url": "/bookstoscrapeall/<titel>",
                "description": "Söker efter böcker med user input i titeln. Returnerar matchningar"
            },
            "POST add_book": {
                "method": "POST",
                "url": "/bookstoscrapeall/",
                "description": "Lägg till en ny bok. Skicka med en JSON-body enligt exemplet nedan.",
                "example_body": {
                    "title": "TITEL",
                    "rating": "___ Stars",
                    "price_sek": "DITT PRIS HÄR",
                    "link": "DIN LÄNK HÄR"
                }
            },
            "PUT update_book": {
                "method": "PUT",
                "url": "/bookstoscrapeall/<titel>",
                "description": "Uppdaterar info för en specifik bok."
            },
            "DELETE delete_book": {
                "method": "DELETE",
                "url": "/bookstoscrapeall/<titel>",
                "description": "Tar bort en specifik bok."
            },
            "DELETE delete_file": {
                "method": "DELETE",
                "url": "/file/<string:date>",
                "description": "Tar bort en specifik fil."
            }
        }
    })