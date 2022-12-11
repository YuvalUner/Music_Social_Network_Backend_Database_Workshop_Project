from repositories import ArtistsRepository
from flask import Blueprint, jsonify, request

artists_routes = Blueprint('artists', __name__)


@artists_routes.route('/login', methods=["POST"])
def check_artist_in_db(artist_name: str):
    if not ArtistsRepository.get_instance().login_artist_check(artist_name):
        return jsonify({"result": False}), 404
    return jsonify({"result": True}), 200


@artists_routes.route('/add', methods=["POST"])
def add_new_artist():
    ArtistsRepository.get_instance().add_artist(request.json["name"], request.json["password"])
    return jsonify({"res": "OK"}), 201
