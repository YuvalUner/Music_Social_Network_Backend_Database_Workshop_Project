from flask import Blueprint, jsonify, request
from repositories.favorite_songs import FavoriteSongsRepository
from routes.songs import SongWithArtistAndAlbum

favorite_songs_routes = Blueprint('favorite_songs_routes', __name__)

@favorite_songs_routes.route('/', methods=['POST'])
def add_favorite_song():
    try:
        song_name = request.json['song_name']
        album_name = request.json['album_name']
        artist_name = request.json['artist_name']
        FavoriteSongsRepository.get_instance().add_favorite_song(song_name, album_name, artist_name)
        return jsonify({'message': 'Song added to favorites.'}), 201
    except Exception as e:
        return jsonify({'Error': "Illegal query or song is already in your favorites or song does not exist"}), 400


@favorite_songs_routes.route('/<artist_name>', methods=['GET'])
def get_favorite_songs(artist_name: str):
    try:
        songs = FavoriteSongsRepository.get_instance().get_favorite_songs(artist_name)
        song_list = []
        for song in songs:
            song_item = SongWithArtistAndAlbum(
                artist_name=song[0],
                album_name=song[2],
                song_name=song[4],
                duration=song[5],
                song_key=song[6],
                release_date=song[7],
                is_major=song[8],
                energy=song[9],
                song_spotify_id=song[10],
                album_id=""
            )
            if song_item not in song_list:
                song_list.append(song_item)
            else:
                song_list[song_list.index(song_item)].add_artist(song[0])
        return jsonify([song.to_dict() for song in song_list]), 200
    except Exception as e:
        return jsonify({'Error': "Illegal query"}), 400