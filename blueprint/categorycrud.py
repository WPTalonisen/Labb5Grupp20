from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime

# Skapar en ny blueprint specifik för CRUD-operationer på kategorier
category_crud_bp = Blueprint('category_crud_bp', __name__)


def get_specific_category_filename(category_name):
    """Hjälpfunktion för att få fram rätt filnamn baserat på kategori och datum."""
    safe_category = category_name.lower().replace(" ", "_")
    today_date = datetime.now().strftime("%Y-%m-%d")
    return f"{safe_category}_{today_date}.json"


# LÄGG TILL en bok i en specifik kategori (POST)
@category_crud_bp.route('/<string:category_name>/books', methods=['POST'])
def add_category_book(category_name):
    filename = get_specific_category_filename(category_name)

    if not os.path.exists(filename):
        return jsonify(
            {"error": f"Dagens fil för '{category_name}' saknas. Gör en GET-request först för att skrapa den."}), 404

    new_book = request.get_json()
    if not new_book:
        return jsonify({"error": "Ingen JSON-data skickades med"}), 400

    # Läs den specifika filen
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Lägg till boken (kategorifilerna använder nyckeln "books" istället för "book_list")
    data["books"].append(new_book)
    data["count"] = len(data["books"])

    # Spara
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Boken lades till i {category_name}!", "book": new_book}), 201


# UPPDATERA en bok i en specifik kategori (PUT)
@category_crud_bp.route('/<string:category_name>/books/<string:title>', methods=['PUT'])
def update_category_book(category_name, title):
    filename = get_specific_category_filename(category_name)

    if not os.path.exists(filename):
        return jsonify({"error": f"Dagens fil för '{category_name}' saknas."}), 404

    updated_info = request.get_json()
    if not updated_info:
        return jsonify({"error": "Ingen uppdateringsdata skickades"}), 400

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Leta rätt på boken och uppdatera
    for book in data["books"]:
        if book.get("title", "").lower() == title.lower():
            book.update(updated_info)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            return jsonify({"message": "Bokens information uppdaterad!", "book": book}), 200

    return jsonify({"error": f"Boken '{title}' hittades inte i denna kategori"}), 404


# TA BORT en bok från en specifik kategori (DELETE)
@category_crud_bp.route('/<string:category_name>/books/<string:title>', methods=['DELETE'])
def delete_category_book(category_name, title):
    filename = get_specific_category_filename(category_name)

    if not os.path.exists(filename):
        return jsonify({"error": f"Dagens fil för '{category_name}' saknas."}), 404

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    initial_count = data.get("count", 0)

    # Filtrera bort boken som matchar titeln
    data["books"] = [
        book for book in data["books"]
        if book.get("title", "").lower() != title.lower()
    ]

    if len(data["books"]) == initial_count:
        return jsonify({"error": "Boken hittades inte"}), 404

    # Uppdatera antal och spara
    data["count"] = len(data["books"])

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Boken '{title}' togs bort från {category_name}"}), 200