from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime

book_crud_bp = Blueprint('book_crud_bp', __name__)


# Hittar dagens datum och lägger till det i filnamnet
def get_todays_filename():
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"bookstoscrapeall_cache_{today_date}.json"

    return filename


# Gör det lättare att läsa filen
def read_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None

# Gör det lättare att skriva till filen
def write_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# ROUTES FÖR POST PUT OCH DELETE


# Lägger till bok till JSON fil
@book_crud_bp.route('/', methods=['POST'])
def add_book():
    filename = get_todays_filename()
    data = read_json(filename)

    if not data:
        return jsonify({'error': 'Dagens fil finns inte ännu. Gör en GET request för att skrapa och skapa en ny.'}), 404

    new_book = request.get_json()

    required_fields = ["title", "rating", "price", "link"]

    if not new_book:
        return jsonify({"error": "Ingen ny data skickades"}), 400

    data["book_list"].append(new_book)
    data["count"] = len(data["book_list"])

    write_json(data, filename)
    return jsonify({"message": "Boken lades till!", "book": new_book}), 200

# Ändrar information om bok i JSON fil
@book_crud_bp.route('/<string:title>', methods=['PUT'])
def update_book(title):
    filename = get_todays_filename()
    data = read_json(filename)

    if not data:
        return jsonify({'error': 'Dagens fil finns inte ännu. Gör en GET request för att skrapa och skapa en ny.'}), 404

    updated_book_info = request.get_json()

    for book in data["book_list"]:
        if book["title"] == title:
            book.update(updated_book_info)
            write_json(data, filename)
            return jsonify({"message": "Bokens information uppdaterad!", "book": book}), 200
    return jsonify({"error": "Boken hittades inte"}), 400

# Tar bort bok från JSON fil
@book_crud_bp.route('/<string:title>', methods=['DELETE'])
def delete_book(title):
    filename = get_todays_filename()
    data = read_json(filename)
    if not data:
        return jsonify({"error": "Dagens fil saknas"}), 404

    initial_count = data["count"]
    # Filtrera bort boken som matchar titeln
    data["book_list"] = [
        book for book in data["book_list"]
        if book.get("title", "").lower() != title.lower()
    ]

    if len(data["book_list"]) == initial_count:
        return jsonify({"message": "Boken hittades inte"}), 404
    data["count"] = len(data["book_list"])
    write_json(data, filename)
    return jsonify({"message": f"Boken '{title} togs bort från JSON filen"}), 200

# Tar bort hel JSON fil
@book_crud_bp.route('/file/<string:date>', methods=['DELETE'])
def remove_file(date):
    filename = f"bookstoscrapeall_cache{date}.json"

    if os.path.exists(filename):
        os.remove(filename)
        return jsonify({"message": f"{filename} har tagits bort"}), 200
    else:
        return jsonify({"message": {f"{filename} hittades inte"}})


# Hittar bok titel efter user input
@book_crud_bp.route('/<string:title>', methods=['GET'])
def find_book(title):
    filename = get_todays_filename()
    data = read_json(filename)

    if not data:
        return jsonify({'error': 'Dagens fil finns inte ännu. Gör en GET request för att skrapa och skapa en ny.'}), 404

    book = data.get("title")

    matched_books =  []

    for book in data["book_list"]:
        if title.lower() in book.get("title", "").lower():
            matched_books.append(book)

    if matched_books:
        return jsonify({
            "message": f"Hittade {len(matched_books)} bok/böcker som matchar {title}",
            "results": matched_books
        }), 200
    else:
        return jsonify({"error": f"Hittade ingen bok som matchar {title}"}), 404