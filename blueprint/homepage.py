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
                "url": "/categories/<kategori>",
                "description": "Hämtar specifik kategori från user input och skrapar den sidan, lagrar sedan alla böcker i separat fil."
            },
            "POST add_category_book": {
                "method": "POST",
                "url": "/categories/<kategori>/books",
                "description": "Lägger till en ny bok i en specifik kategorifil.",
                "example_body": {
                    "title": "DIN TITEL HÄR ",
                    "rating": "___ Stars",
                    "price": "DITT PRIS HÄR kr",
                    "link": "DIN LÄNK HÄR"
                }
            },
            "PUT update_category_book": {
                "method": "PUT",
                "url": "/categories/<kategori>/books/<titel>",
                "description": "Uppdaterar info för en specifik bok inuti en specifik kategori."
            },
            "DELETE delete_category_book": {
                "method": "DELETE",
                "url": "/categories/<kategori>/books/<titel>",
                "description": "Tar bort en specifik bok från en specifik kategori."
            },
            "GET all_books": {
                "method": "GET",
                "url": "/bookstoscrapeall/",
                "description": "VARNING: Hämtar ALLA böcker från dagens cache eller skrapar nytt."
            },
            "GET find_book": {
                "method": "GET",
                "url": "/bookstoscrapeall/<titel>",
                "description": "Söker efter böcker med user input i titeln i stora filen. Returnerar matchningar"
            },
            "POST add_book": {
                "method": "POST",
                "url": "/books/",
                "description": "Lägg till en ny bok i stora filen. Skicka med en JSON-body enligt exemplet nedan.",
                "example_body": {
                    "title": "TITEL",
                    "rating": "___ Stars",
                    "price": "DITT PRIS HÄR kr",
                }
            },
            "PUT update_book": {
                "method": "PUT",
                "url": "/books/<titel>",
                "description": "Uppdaterar info för en specifik bok i huvudfilen."
            },
            "DELETE delete_book": {
                "method": "DELETE",
                "url": "/books/<titel>",
                "description": "Tar bort en specifik bok från huvudfilen."
            },
            "DELETE delete_file": {
                "method": "DELETE",
                "url": "/books/file/<string:date>",
                "description": "Tar bort en specifik fil."
            }
        }
    })