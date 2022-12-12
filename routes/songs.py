from flask import Blueprint, jsonify

from repositories.songs import SongRepository

songs_routes = Blueprint('songs', __name__)


@songs_routes.route('/approx/<song_name>', methods=['GET'])
def approx_song_search_with_artist_and_album(song_name: str):
    songs = SongRepository.get_instance().approx_song_search_with_artist_and_album(song_name)
    return jsonify([{"song_name": song[0],
                     "duration": song[1],
                     "song_key": song[2],
                     "release_date": song[3],
                     "is_major": song[4],
                     "energy": song[5],
                     "song_spotify_id": song[6],
                     "artist_name": song[7],
                     "album_id": song[8],
                     "album_name": song[9]} for song in songs])
