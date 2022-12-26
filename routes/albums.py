from flask import Blueprint, jsonify
from repositories import AlbumsRepository

albums_routes = Blueprint('albums', __name__)


@albums_routes.route('/', methods=["GET"])
def get_all_albums():
    albums = AlbumsRepository.get_instance().get_all_albums()
    return jsonify([{"album_id": album[0],
                     "album_name": album[1],
                     "album_spotify_id": album[2]} for album in albums])


@albums_routes.route('/all_albums_grades', methods=["GET"])
def get_all_albums_ratings():
    res = AlbumsRepository.get_instance().get_all_albums_ratings()
    return jsonify([{"album_id": rec[0],
                     "album_name": rec[1],
                     "album_rating": rec[2]} for rec in res])
