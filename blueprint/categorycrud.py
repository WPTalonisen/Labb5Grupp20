from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime

category_crud_bp = Blueprint('category_crud_bp', __name__)


# Tar den här istället för att skriva det flera gånger i kommande funktioner
def get_specific_category_filename(category_name):
    category = category_name.lower().replace(" ", "_")
    today_date = datetime.now().strftime("%Y-%m-%d")
    return f"{category}_{today_date}.json"


# Lägg till bok
@category_crud_bp.route('/<string:category_name>', methods=['POST'])
def add_category_book(category_name):
    filename = get_specific_category_filename(category_name)

    if not os.path.exists(filename):
        return jsonify(
            {"error": f"Dagens fil för '{category_name}' saknas. Gör en GET-request först för att skrapa den."}), 404

    new_book = request.get_json()
    if not new_book:
        return jsonify({"error": "Ingen JSON-data skickades med"}), 400

    required_fields = ['title', 'rating', 'price']

    # Kollar så att alla info som behövs finns
    for field in required_fields:
        if field not in new_book:
            return jsonify({"error": f"Fältet '{field}' krävs. Besök \"127.0.0.1:5000\" för hjälp."}), 400

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Lägg till boken
    data["books"].append(new_book)
    data["count"] = len(data["books"])

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Boken lades till i {category_name}!", "book": new_book}), 201


# Uppdatera bok
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


# Ta bort bok från lista
@category_crud_bp.route('/<string:category_name>/<string:title>', methods=['DELETE'])
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