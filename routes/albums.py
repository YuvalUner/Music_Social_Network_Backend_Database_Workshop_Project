import string

from flask import Blueprint, jsonify, request, app
from repositories.albums import AlbumsRepository
from repositories.recommendations import RecommendationsRepository, RecommendationsDataProcessing
import math

albums_routes = Blueprint('albums', __name__)


@albums_routes.route('/add/', methods=["POST"])
def add_album():
    """
    input: JSON: {'album_name' = NAME, 'album_spotify_id' = ID}
    """
    try:
        # Pull all the values from the request
        # album_id = int(request.json['album_id']) AUTO INSERTION
        album_name = request.json['album_name']
        album_spotify_id = request.json['album_spotify_id']
        AlbumsRepository.get_instance().add_album(album_name, album_spotify_id)
        return jsonify({'message': 'Album added successfully'}), 201
    except TypeError:
        return jsonify({'error': "Illegal query"}), 400
    except Exception as e:
        return jsonify({'error': "Album already exists in the system"}), 400


@albums_routes.route('/add_artist_connector/', methods=["POST"])
def add_artist_album_connector():
    try:
        artist_id = request.json['artist_id']
        album_id = request.json['album_id']
        AlbumsRepository.get_instance().add_artist_connection(album_id, artist_id)
        return jsonify({'message': 'Album-Artist connector added successfully'}), 201

    except TypeError:
        return jsonify({'error': "Illegal query"}), 400
    except Exception as e:
        return jsonify({'error': "Album or Artist does not exist, or has already been inserted."}), 400



@albums_routes.route('/', methods=["GET"])
def get_all_albums():
    """
    WEB API
    Get all albums with their ratings.
    :return: (album_id, album_name, rating)
    """
    albums = AlbumsRepository.get_instance().get_all_albums()
    return jsonify([{"album_id": album[0],
                     "album_name": album[1],
                     "album_spotify_id": album[2]} for album in albums])


# CHANGE: request.args.get -> route param
@albums_routes.route('/search/<album_name>', methods=["GET"])
def get_album_by_name(album_name: str):
    """
    WEB API
    Get all albums with their ratings.
    :return: (album_id, album_name, rating)
    """
    # album_name = request.args.get("name")
    album = AlbumsRepository.get_instance().get_album_by_name(album_name)
    return jsonify({"album_id": album[0][0],
                     "album_name": album[0][1],
                     "album_spotify_id": album[0][2],
                     "rating": album[0][3]})



@albums_routes.route('/all_albums_grades', methods=["GET"])
def get_all_albums_ratings():
    """
    WEB API
    Get all albums with their ratings.
    :return: (album_id, album_name, rating)
    """
    res = AlbumsRepository.get_instance().get_all_albums_ratings()
    return jsonify([{"album_id": rec[0],
                     "album_name": rec[1],
                     "album_rating": rec[2]} for rec in res])


@albums_routes.route('/get_x_highest_ranked_albums', methods=["GET"])
def get_x_highest_ranked_albums():
    """
    WEB API
    Get top NUM albums with their ratings.
    :param num: num of songs to return.
    :return: (album_id, album_name, rating)
    """
    num = request.args.get('num')
    res = AlbumsRepository.get_instance().get_x_highest_ranked_albums(num)
    return jsonify([{"album_id": rec[0],
                     "album_name": rec[1],
                     "album_rating": rec[2]} for rec in res])


#TODO: Figure out how this stuff works, return types etc...
# Testing for: /The Big Boss/10
@albums_routes.route('/get_reccomendations/<username>/<limit>', methods=["GET"])
def get_album_recommendations(limit: int, username: string):
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
        # TEST RESULT: dict per Genre
        # {'Indie':
            #   [(513737, 'I Wanna Have Some Fun', 235933, 7, datetime.date(1992, 1, 1), 1, 0.58, '2MLtib2ulZ6eeu4zTToYr7', 158678, 'Michael Percy', "'1PWS3ACXatxz3XOb6vvdja'", 14491, 'Greatest Hits', '5dXjkwmrW65p0jUXAoQ8kU'),
        #   'Soul Music': [...] ...
        if recommendations is None or len(recommendations) == 0:
            return jsonify({'error': "No recommendations found"}), 404
        total_score = 0
        # Calculate relative scores of each genre
        for genre in best_genres:
            total_score += best_genres[genre]
        relative_scores = {g: math.ceil((best_genres[g] / total_score) * limit) for g in best_genres}
        # TEST RESULT: relative_scores = {'Indie': 5, 'Soul Music': 3, 'Pop/Rock': 3}

        albums_by_genres = {}
        for g in best_genres:
            albums_by_genres[g] = []
            for i in range(relative_scores[g]):
                # KILL ME.
                # album = AlbumsRepository.get_instance().get_album_by_name(recommendations[g][i][12])
                res = {"album_id": recommendations[g][i][11],
                        "album_name": recommendations[g][i][12],
                        "album_spotify_id": recommendations[g][i][13]}
                albums_by_genres[g].append(res)

        # with app.app_context(): recommendations[g][i][12]
        #    albums_by_genres = {g: get_album_by_name(recommendations[g][13])[:relative_scores[g]]
        #                        for g in best_genres}
        # albums_by_genre =
        # SongWithArtistAndAlbum.from_list_as_dicts(recommendations[g][:relative_scores[g]]

        return albums_by_genres, 200

    except TypeError:
        return jsonify({'error': "Illegal argument - must be an integer"}), 404
    except Exception as e:
        return jsonify({'error': "Illegal query"}), 500

if __name__ == "__main__":
    #print(get_album_recommendations(10, "The Big Boss"))
    pass