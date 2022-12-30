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
    try:
        x = request.json
        ArtistsRepository.get_instance().add_artist(request.json["name"], request.json["password"])
        return jsonify({"res": "OK"}), 201
    except Exception as e:
        return jsonify({"res": "Username already exists"}), 400


@artists_routes.route('/<int:artist_id>/albums', methods=["GET"])
def get_artist_albums(artist_id: int):
    albums = ArtistsRepository.get_instance().get_artist_albums(artist_id)
    return jsonify({"albums": albums}), 200


@artists_routes.route('/albums/<artist_name>', methods=["GET"])
def get_artist_albums_by_name(artist_name: str):
    albums = ArtistsRepository.get_instance().get_artist_albums_by_name(artist_name)
    return jsonify({"albums": albums}), 200


@artists_routes.route('/rating/<artist_name>', methods=["GET"])
def get_artist_rating(artist_name: str):
    rating = ArtistsRepository.get_instance().get_artist_rating(artist_name)
    return jsonify({"rating": rating}), 200


@artists_routes.route('/top_rated/<int:n>', methods=["GET"])
def get_top_rated_artists(n: int):
    n_top_rated = ArtistsRepository.get_instance().get_highest_rated_artists(n)
    return jsonify({"top_rated_artists": n_top_rated}), 200


@artists_routes.route('/spotify_id/<artist_name>', methods=["GET"])
def get_artist_spotify_id(artist_name: str):
    try:
        spotify_id = ArtistsRepository.get_instance().get_artist_by_name(artist_name)[3]
        return jsonify({"spotify_id": spotify_id}), 200
    except Exception as e:
        return jsonify({"Error": "Not found"}), 404
