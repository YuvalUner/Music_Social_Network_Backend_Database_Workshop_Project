from flask import Blueprint, jsonify, request

from repositories.songs import SongRepository

songs_routes = Blueprint('songs', __name__)


class SongAbstract:

    def to_dict(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        return str(self.to_dict())


class Song(SongAbstract):

    def __init__(self, song_name, album_id, duration, song_key, release_date, is_major, energy, song_spotify_id):
        self.song_name = song_name
        self.duration = duration
        self.song_key = song_key
        self.release_date = release_date
        self.is_major = is_major
        self.energy = energy
        self.song_spotify_id = song_spotify_id
        self.album_id = album_id

    def to_dict(self):
        return {
            'song_name': self.song_name,
            'album_id': self.album_id,
            'duration': self.duration,
            'song_key': self.song_key,
            'release_date': self.release_date,
            'is_major': self.is_major,
            'energy': self.energy,
            'song_spotify_id': self.song_spotify_id
        }

    def __eq__(self, other):
        return self.song_spotify_id == other.song_spotify_id

class SongWithRating(Song):

    def __init__(self, song_name, album_id, duration, song_key, release_date, is_major, energy, song_spotify_id, rating):
        super().__init__(song_name, album_id, duration, song_key, release_date, is_major, energy, song_spotify_id)
        self.rating = rating

    def to_dict(self):
        return {
            'song_name': self.song_name,
            'album_id': self.album_id,
            'duration': self.duration,
            'song_key': self.song_key,
            'release_date': self.release_date,
            'is_major': self.is_major,
            'energy': self.energy,
            'song_spotify_id': self.song_spotify_id,
            'rating': self.rating
        }



class SongWithArtistAndAlbum(Song):
    def __init__(self, song_name, duration, song_key, release_date, is_major, energy, song_spotify_id, artist_name,
                 album_id, album_name):
        super().__init__(song_name, album_id, duration, song_key, release_date, is_major, energy, song_spotify_id)
        self.artists = []
        self.artists.append(artist_name)
        self.album_name = album_name

    def to_dict(self):
        return {
            'song_name': self.song_name,
            'duration': self.duration,
            'song_key': self.song_key,
            'release_date': self.release_date,
            'is_major': self.is_major,
            'energy': self.energy,
            'song_spotify_id': self.song_spotify_id,
            'artists': self.artists,
            'album_id': self.album_id,
            'album_name': self.album_name
        }

    def add_artist(self, artist_name):
        self.artists.append(artist_name)



@songs_routes.route('/approx/<song_name>', methods=['GET'])
def approx_song_search_with_artist_and_album(song_name: str):
    """
    Returns a list of songs that are like the given song name.
    :param song_name: the name of the song
    :return: JSON list of songs that are like the given song name with artist and album
    """
    try:
        songs = SongRepository.get_instance().approx_song_search_with_artist_and_album(song_name)
        if songs is None or len(songs) == 0:
            return jsonify({'error': 'No songs found'}), 404
        song_list = []
        for song in songs:
            song_item = SongWithArtistAndAlbum(song[0], song[1], song[2], song[3], song[4], song[5], song[6], song[7],
                                               song[8], song[9])
            if song_item not in song_list:
                song_list.append(song_item)
            else:
                song_list[song_list.index(song_item)].add_artist(song[7])
        return jsonify([song.to_dict() for song in song_list]), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/exact/<song_name>', methods=['GET'])
def exact_song_search_with_artist_and_album(song_name: str):
    """
    Returns a list of songs with the given name
    :param song_name: the name of the song
    :return: JSON list of songs with all their details and the artists and album name
    """
    try:
        songs = SongRepository.get_instance().exact_song_search_with_artist_and_album(song_name)
        if songs is None or len(songs) == 0:
            return jsonify({'error': "No songs found"}), 404
        song_list = []
        for song in songs:
            song_item = SongWithArtistAndAlbum(song[0], song[1], song[2], song[3], song[4], song[5], song[6], song[7],
                                               song[8], song[9])
            if song_item not in song_list:
                song_list.append(song_item)
            else:
                song_list[song_list.index(song_item)].add_artist(song[7])
        return jsonify([song.to_dict() for song in song_list]), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/add/', methods=['POST'])
def add_song():
    """
    Adds a song to the database
    :return: 201 on success, 400 on failure
    """
    try:
        song_name = request.json['song_name']
        duration = int(request.json['duration'])
        song_key = request.json['song_key']
        release_date = request.json['release_date']
        is_major = int(request.json['is_major'])
        energy = float(request.json['energy'])
        song_spotify_id = request.json['song_spotify_id']
        album = request.json['album']
        artist = request.json['artist']
        SongRepository.get_instance().add_song(song_name, album, artist, song_spotify_id, duration, song_key,
                                               release_date, is_major, energy)
        return jsonify({'message': 'Song added successfully'}), 201
    except TypeError:
        return jsonify({'error': "Illegal query"}), 400
    except Exception as e:
        return jsonify({'error': "Song already exists in this album or the artist or album do not exist"}), 400


@songs_routes.route('/get_by_name_and_album/<song_name>/<album_name>', methods=['GET'])
def get_song_by_name_and_album(song_name: str, album_name: str):
    """
    Get a song by its name and album name
    :param song_name: name of the song to get
    :param album_name: name of the album it belongs to.
    :return: A JSON object with the song's details
    """
    try:
        song = SongRepository.get_instance().get_song_by_song_name_and_album_name(song_name, album_name)
        if song is None or len(song) == 0:
            return jsonify({'error': "Song not found"}), 404
        song = song[0]
        song_item = Song(song[1], song[2], song[3], song[4], song[5], song[6], song[7], song[8])
        return jsonify(song_item.to_dict()), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/get_in_album/<album_name>', methods=['GET'])
def get_songs_in_album(album_name: str):
    """
    Returns all songs in an album
    :param album_name: name of the album
    :return: JSON with all songs in the album
    """
    try:
        songs = SongRepository.get_instance().get_songs_in_album(album_name)
        if songs is None or len(songs) == 0:
            return jsonify({'error': "Album does not exist"}), 404
        song_list = []
        for song in songs:
            song_item = Song(song[1], song[2], song[3], song[4], song[5], song[6], song[7], song[8])
            song_list.append(song_item)
        return jsonify([song.to_dict() for song in song_list]), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/song_rating/<song_name>/<album_name>', methods=['GET'])
def get_song_rating(song_name: str, album_name: str):
    """
    Returns the average rating of a song
    :param song_name: the name of the song
    :param album_name: name of the album the song belongs to
    :return: A JSON object with the average rating of the song
    """
    try:
        song = SongRepository.get_instance().get_song_rating(song_name, album_name)
        if song is None or len(song) == 0:
            return jsonify({'error': "Song not found"}), 404
        song_rating = float(song[0][0])
        return jsonify({'rating': song_rating}), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/top_songs/<number_of_songs>', methods=['GET'])
def get_top_songs(number_of_songs: int):
    """
    Returns the top songs in the database
    :param number_of_songs: the number of songs to get.
    :return: JSON of the top songs
    """
    try:
        number_of_songs = int(number_of_songs)
        songs = SongRepository.get_instance().get_top_rated_songs(number_of_songs)
        if songs is None or len(songs) == 0:
            return jsonify({'error': "Our database appears to have been gone up in flames."
                                     " We deeply apologize for the inconvenience."}), 500
        song_list = []
        for song in songs:
            song_item = SongWithRating(song[1], song[2], song[3], song[4], song[5], song[6], song[7], song[8],
                                       float(song[9]))
            song_list.append(song_item)
        return jsonify([song.to_dict() for song in song_list]), 200
    except TypeError:
        return jsonify({'error': "Illegal argument - must be an integer"}), 404
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500

@songs_routes.route('/top_songs_per_year/<number_of_songs>/<year>', methods=['GET'])
def get_top_songs_per_year(number_of_songs: int, year: str):
    """
    Returns the top songs of a given year
    :param number_of_songs: number of songs to get
    :param year: the year to get the songs from
    :return: JSON of the top songs of the given year
    """
    try:
        number_of_songs = int(number_of_songs)
        year += '-01-01'
        songs = SongRepository.get_instance().get_top_rated_songs_per_year(year, number_of_songs)
        if songs is None or len(songs) == 0:
            return jsonify({'error': "No songs found for the specified year"}), 500
        song_list = []
        for song in songs:
            song_item = SongWithRating(song[1], song[2], song[3], song[4], song[5], song[6], song[7], song[8],
                                       float(song[9]))
            song_list.append(song_item)
        return jsonify([song.to_dict() for song in song_list]), 200
    except TypeError:
        return jsonify({'error': "Illegal argument - must be an integer"}), 404
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500

@songs_routes.route('/get_reccomendations/<limit>/<username>', methods=['GET'])
def get_reccomendations(limit: int, username: str):
    """
    Returns a list of reccomendations for the user
    :param limit: the number of songs to get
    :param username: the username of the user
    :return: JSON of the reccomendations
    """
    try:
        limit = int(limit)
        song_repo = SongRepository.get_instance()
        liked_songs = song_repo.get_info_on_liked_songs(username)
        user_preferred_genres = []
        user_preferred_artists = []
        user_preferred_years = []
        user_preferred_albums = []
        user_preferred_energy = []
        user_preferred_key = []
        user_preferred_duration = []
        for song in liked_songs:
            rating = song[12]
            genre = song[0]
            artist = song[1]
            album = song[2]
            duration = song[6]
            song_key = song[7]
            year = song[8]
            is_major = song[9]
            energy = song[10]
            user_preferred_genres.append((genre, rating))
            user_preferred_artists.append((artist, rating))
            user_preferred_years.append((year, rating))
            user_preferred_albums.append((album, rating))
            user_preferred_energy.append((energy, rating))
            user_preferred_key.append((song_key, is_major, rating))
            user_preferred_duration.append((duration, rating))


        if liked_songs is None or len(liked_songs) == 0:
            return jsonify({'error': "No songs found"}), 500
        song_list = []
        for song in liked_songs:
            song_item = SongWithRating(song[1], song[2], song[3], song[4], song[5], song[6], song[7], song[8],
                                       float(song[9]))
            song_list.append(song_item)
        return jsonify([song.to_dict() for song in song_list]), 200
    except TypeError:
        return jsonify({'error': "Illegal argument - must be an integer"}), 404
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500