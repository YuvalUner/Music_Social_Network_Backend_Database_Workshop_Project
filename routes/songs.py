import math
import random
from typing import List

from flask import Blueprint, jsonify, request

from repositories.songs import SongRepository
from repositories.recommendations import RecommendationsRepository, RecommendationsDataProcessing

songs_routes = Blueprint('songs', __name__)


class SongAbstract:

    def to_dict(self) -> dict:
        """
        :return: Returns a dictionary representation of the object.
        """
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        return str(self.to_dict())


class Song(SongAbstract):
    """
    A song object that represents a song in the database.
    Only has the fields that are in the songs table.
    """

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
    """
    A song object that represents a song in the database.
    Has the fields in the song table + the rating.
    """

    def __init__(self, song_name, album_id, duration, song_key, release_date, is_major, energy, song_spotify_id,
                 rating):
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
    """
    A song object that represents a song in the database.
    Has the fields in the song table + the song's album and artists.
    """
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


    def add_artist(self, artist_name) -> None:
        """
        Adds an artist to the song's list of artists.
        :param artist_name: the artist to add.
        """
        self.artists.append(artist_name)

    @staticmethod
    def from_list(song_list: list) -> list:
        """
        Creates a list of SongWithArtistAndAlbum objects from a list of songs.
        The format of each song in the list needs to be that of the one returned from the recommendations repository's
        get recommendations.
        :param song_list: the list of songs
        :return: A list of SongWithArtistAndAlbum objects.
        """
        songs = []
        for song in song_list:
            songs.append(SongWithArtistAndAlbum(song[1], song[2], song[3], song[4], song[5], song[6], song[7],
                                                song[9], song[11], song[12]))
        return songs

    @staticmethod
    def from_list_as_dicts(song_list: list) -> List[dict]:
        """
        Like from_list, but converts the list of SongWithArtistAndAlbum objects to a list of dictionaries.
        :param song_list: see from_list
        :return: dict representation of the list of SongWithArtistAndAlbum objects.
        """
        songs = SongWithArtistAndAlbum.from_list(song_list)
        return [song.to_dict() for song in songs]


class SongWithFullInfo(SongWithArtistAndAlbum):

    def __init__(self, song_name, duration, song_key, release_date, is_major, energy, song_spotify_id, artist_name,
                 album_name, rating, album_id=0):
        super().__init__(song_name, duration, song_key, release_date, is_major, energy, song_spotify_id, artist_name,
                         album_id, album_name)
        self.rating = rating

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
            'album_name': self.album_name,
            'rating': self.rating
        }


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
            # Song already exists but appeared under a different artist.
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
            # Song already exists but appeared under a different artist
            else:
                song_list[song_list.index(song_item)].add_artist(song[7])
        return jsonify([song.to_dict() for song in song_list]), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/add', methods=['POST'])
def add_song():
    """
    Adds a song to the database.
    :return: 201 on success, 400 on failure
    """
    try:
        # Pull all the values from the request
        song_name = request.json['song_name']
        duration = int(request.json['duration'])
        song_key = request.json['song_key']
        release_date = request.json['release_date']
        is_major = int(request.json['is_major'])
        energy = float(request.json['energy'])
        song_spotify_id = request.json['song_spotify_id']
        album_name = request.json['album_name']
        artist_name = request.json['artist_name']
        SongRepository.get_instance().add_song(song_name, album_name, artist_name, song_spotify_id, duration, song_key,
                                               release_date, is_major, energy)
        return jsonify({'message': 'Song added successfully'}), 201
    except TypeError:
        return jsonify({'error': "Illegal query"}), 400
    except Exception as e:
        print(e)
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
        # This error should only happen if the album does not exist, as an album must have some song in it.
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
        song_rating = SongRepository.get_instance().get_song_rating(song_name, album_name)[0][0]
        if song_rating is None:
            return jsonify({'error': "Song not found"}), 404
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
        # This is an error that should never happen, as it always returns something if the DB is not empty.
        # Hence, the error for that is phrased as such.
        if songs is None or len(songs) == 0:
            return jsonify({'error': "Our database appears to have been gone up in flames."
                                     " We deeply apologize for the inconvenience."}), 500
        song_list = []
        for song in songs:
            song_item = SongWithFullInfo(
                artist_name=song[0],
                album_name=song[1],
                song_name=song[2],
                duration=song[3],
                song_key=song[4],
                release_date=song[5],
                is_major=song[6],
                energy=song[7],
                song_spotify_id=song[8],
                rating=song[9]
            )
            if song_item not in song_list:
                song_list.append(song_item)
            else:
                song_list[song_list.index(song_item)].add_artist(song[0])
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
        # Make the year a value that can be processed by MySql's STR_TO_DATE function
        year += '-01-01'
        songs = SongRepository.get_instance().get_top_rated_songs_per_year(year, number_of_songs)
        if songs is None or len(songs) == 0:
            return jsonify({'error': "No songs found for the specified year"}), 404
        song_list = []
        # Convert the songs to song objects
        for song in songs:
            song_item = SongWithFullInfo(
                artist_name=song[0],
                album_name=song[1],
                song_name=song[2],
                duration=song[3],
                song_key=song[4],
                release_date=song[5],
                is_major=song[6],
                energy=song[7],
                song_spotify_id=song[8],
                rating=song[9]
            )
            if song_item not in song_list:
                song_list.append(song_item)
            else:
                song_list[song_list.index(song_item)].add_artist(song[0])
        return jsonify([song.to_dict() for song in song_list]), 200
    except TypeError:
        return jsonify({'error': "Illegal argument - must be an integer"}), 404
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/get_reccomendations/<username>/<limit>', methods=['GET'])
def get_recommendations(limit: int, username: str):
    """
    Returns a list of reccomendations for the user
    :param limit: the number of songs to get
    :param username: the username of the user
    :return: JSON of the reccomendations
    """
    try:
        # COPY
        limit = int(limit)
        # Get info about the user's preferences
        recommendations_rep = RecommendationsRepository.get_instance()
        recommendations_info = recommendations_rep.get_recommendation_info_by_liked_songs(username)
        if recommendations_info is None or len(recommendations_info) == 0:
            return jsonify({'error': "No recommendations found"}), 404
        # Process the preferences to get the user's top 3 genres
        best_genres = RecommendationsDataProcessing.get_best_genres(recommendations_info, 3)
        # Get recommendations by those genres
        recommendations = recommendations_rep.get_recommendations_by_liked_genres(best_genres, limit)
        if recommendations is None or len(recommendations) == 0:
            return jsonify({'error': "No recommendations found"}), 404
        total_score = 0
        # Calculate relative scores of each genre
        for genre in best_genres:
            total_score += best_genres[genre]
        relative_scores = {g: math.ceil((best_genres[g] / total_score) * limit) for g in best_genres}
        # UP TO HERE
        # Get relative score number of songs per each genre
        songs_by_genres = {g: SongWithArtistAndAlbum.from_list_as_dicts(recommendations[g][:relative_scores[g]])
                           for g in best_genres}
        return jsonify(songs_by_genres), 200
    except TypeError:
        return jsonify({'error': "Illegal argument - must be an integer"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': "Illegal query", "text": str(e)}), 500


@songs_routes.route('/get_max_min_years', methods=['GET'])
def get_max_min_years():
    """
    Returns the max and min years of the songs in the database
    :return: JSON of the max and min years
    """
    try:
        years = SongRepository.get_instance().get_max_and_min_song_years()
        return jsonify({'max_year': years[0], 'min_year': years[1]}), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500


@songs_routes.route('/random/<int:limit>', methods=['GET'])
def get_random(limit: int):
    """
    Returns a list of random songs
    :return:
    """
    try:
        songs = SongRepository.get_instance().get_random(limit)
        song_list = []
        for song in songs:
            song_item = SongWithArtistAndAlbum(
                artist_name=song[0],
                album_name=song[1],
                song_name=song[2],
                duration=song[3],
                song_key=song[4],
                release_date=song[5],
                is_major=song[6],
                energy=song[7],
                song_spotify_id=song[8],
                album_id=0
            )
            if song_item not in song_list:
                song_list.append(song_item)
            else:
                song_list[song_list.index(song_item)].add_artist(song[0])
        return jsonify([song.to_dict() for song in song_list]), 200
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500
