from repositories import ArtistsRepository
from flask import Blueprint, jsonify, request

artists_routes = Blueprint('artists', __name__)


@artists_routes.route('/login', methods=["POST"])
def check_artist_in_db():
    if not ArtistsRepository.get_instance().login_artist_check(request.json["name"],
                                                               request.json["password"]):
        return jsonify({"result": False}), 404
    return jsonify({"result": True}), 200


@artists_routes.route('/add', methods=["POST"])
def add_new_artist():
    ArtistsRepository.get_instance().add_artist(request.json["name"], request.json["password"])
    return jsonify({"res": "OK"}), 201


@artists_routes.route('/<int:artist_id>/albums', methods=["GET"])
def get_artist_albums(artist_id: int):
    albums = ArtistsRepository.get_instance().get_artist_albums(artist_id)
    return jsonify({"albums": albums}), 200


@artists_routes.route('/top_rated/<int:n>', methods=["GET"])
def get_top_rated_artists(n: int):
    n_top_rated = ArtistsRepository.get_instance().get_highest_rated_artists(n)
    return jsonify({"top_rated_artists": n_top_rated}), 200