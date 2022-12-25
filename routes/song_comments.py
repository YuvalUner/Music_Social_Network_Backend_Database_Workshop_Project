from flask import Blueprint, jsonify, request
from repositories.song_comments import CommentsRepository

comment_routes = Blueprint('comments', __name__)


@comment_routes.route('/', methods=['POST'])
def add_comment():
    """
    Adds a comment to a song.
    """
    try:
        song_name = request.json['song_name']
        album_name = request.json['album_name']
        artist_name = request.json['artist_name']
        comment = request.json['comment']
        rating = int(request.json['rating'])
        CommentsRepository.get_instance().add_comment_to_song(song_name, album_name, artist_name, comment, rating)
        return jsonify({'message': 'Comment added successfully.'}), 201
    except TypeError:
        return jsonify({'Error': 'Rating must be an integer.'}), 400
    except Exception as e:
        return jsonify({'Error': "Illegal query or you have already commented on this song"}), 400


@comment_routes.route('/<song_name>/<album_name>', methods=['GET'])
def get_comments(song_name: str, album_name: str):
    """
    Gets all the comments on a song.
    """
    try:
        comments = CommentsRepository.get_instance().get_comments_on_song(song_name, album_name)
        return jsonify([{
            'artist_name': comment[0],
            'comment': comment[1],
            'rating': comment[2]
        } for comment in comments]), 200
    except Exception as e:
        return jsonify({'Error': "Illegal query"}), 400
