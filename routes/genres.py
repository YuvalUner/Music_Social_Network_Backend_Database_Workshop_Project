from flask import Blueprint, jsonify
from repositories import GenresRepository

genres_routes = Blueprint('genres', __name__)


@genres_routes.route('/all', methods=["GET"])
def get_all_genres():
    genres = GenresRepository.get_instance().get_all()
    genre_names = [genre[1] for genre in genres]
    return jsonify(genre_names), 200
