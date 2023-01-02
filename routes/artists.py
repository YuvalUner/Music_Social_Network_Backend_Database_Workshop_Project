import itertools
import math

from repositories import ArtistsRepository
from flask import Blueprint, jsonify, request

from repositories.recommendations import RecommendationsRepository, RecommendationsDataProcessing
from routes.songs import SongWithArtistAndAlbum

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
    return jsonify([{
        "album_id": album[0],
        "album_name": album[1],
        "spotify_id": album[2],
    } for album in albums]), 200


@artists_routes.route('/rating/<artist_name>', methods=["GET"])
def get_artist_rating(artist_name: str):
    rating = ArtistsRepository.get_instance().get_artist_avg_rating(artist_name)
    return jsonify({"rating": rating}), 200


@artists_routes.route('/top_rated/<int:n>', methods=["GET"])
def get_top_rated_artists(n: int):
    n_top_rated = ArtistsRepository.get_instance().get_highest_rated_artists(n)
    return jsonify({"top_rated_artists": n_top_rated}), 200


@artists_routes.route('/spotify_id/<artist_name>', methods=["GET"])
def get_artist_spotify_id(artist_name: str):
    try:
        spotify_id = ArtistsRepository.get_instance().get_artist_by_name(artist_name)[0][3]
        return jsonify({"spotify_id": spotify_id}), 200
    except Exception as e:
        return jsonify({"Error": "Not found"}), 404


@artists_routes.route('link_genre', methods=["POST"])
def link_artist_to_genre():
    try:
        artist_name = request.json["artist_name"]
        genre_name = request.json["genre_name"]
        ArtistsRepository.get_instance().link_artist_to_genre(artist_name, genre_name)
        return jsonify({"res": "OK"}), 201
    except Exception as e:
        return jsonify({"res": "Error"}), 400


@artists_routes.route('/get_reccomendations/<username>/<limit>', methods=['GET'])
def get_recommendations(limit: int, username: str):
    """
    Returns a list of reccomendations for the user
    :param limit: the number of artists to get
    :param username: the username of the user
    :return: JSON of the reccomendations
    """
    try:
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
        # for artists
        relative_scores = {g: math.ceil((best_genres[g] / total_score) * limit * 2) for g in best_genres}
        # Get relative score number of songs per each genre
        song_by_genres = {g: SongWithArtistAndAlbum.from_list_as_dicts(recommendations[g][:relative_scores[g]])
                           for g in best_genres}

        artists_by_genres = {}
        for genre in song_by_genres:
            artists = [song_by_genres[genre][i]["artists"] for i in range(len(song_by_genres[genre]))]
            flatten = list(itertools.chain(*artists))
            recs = list(set(flatten))
            d = []
            for ar in recs:
                d.append({"artist_name": ar})
            artists_by_genres[genre] = d[:limit]

        return jsonify(artists_by_genres), 200
    except TypeError:
        return jsonify({'error': "Illegal argument - must be an integer"}), 404
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500
