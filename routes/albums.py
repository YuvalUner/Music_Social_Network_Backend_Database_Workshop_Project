import string

from flask import Blueprint, jsonify, request, app
from repositories.albums import AlbumsRepository
from repositories.recommendations import RecommendationsRepository, RecommendationsDataProcessing
import math

albums_routes = Blueprint('albums', __name__)


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
            #   (771144, 'Tulisuudelma', 206800, 3, datetime.date(2004, 4, 22), 1, 0.322, '6bpwiDscxy2OSHNZKZ4a85', 155374, 'Topi Sorsakoski', "'2E5oIWJKpGAckSxFSRpcE6'", 33750, 'Unohtumattomat 2', '53c71wbQjzrLisfRGtzTSW'),
            #   (1025578, 'Ghoul Train', 286665, 2, datetime.date(2015, 6, 1), 1, 0.924, '7buWUUYOHnCVI4GcatRpuy', 221867, 'Emily Valentine', "'4Rn4Dlqzi7GEldLS2JqmR0'", 29816, 'Dark Matter', '5zY43e8Ldp5e7uDguRV7nN'),
            #   (696933, 'Ice Cream', 154613, 7, datetime.date(2008, 2, 5), 0, 0.657, '6vmzSbIvPFPKOztNJGiyLU', 147897, 'Mustah F.A.B.', "'6LxHMxSNnU55ZufRUcQi68'", 40710, 'Starters In The Game', '639mPMi50pnsq3k09PlxVh'),
            #   (1348635, "Santa Claus Is Comin' to Town - Live at C.W. Post College, Greenvale, NY - December 1975", 267600, 1, datetime.date(2019, 11, 17), 1, 0.668, '0lsOuWXmFrCB49ykSLzVCF', 1577, 'Martina McBride', None, 88654, "Santa's Happy Hour", '60OpZt3Hw8MMxcHW8e5QTL'),
            #   (920901, 'Audite Me: Composition by Giovanni Felice Sances', 351120, 12, datetime.date(2003, 10, 21), 1, 0.0974, '7knIudAWvPxThkL4u3Gfzq', 149122, 'СБПЧ', "'2lcnX886C4JZUvC4PSC9GE'", 15585, 'Remixes', '5gslwiONYirVmltQvdSLXf'),
            #   (802029, 'Finger Gang', 110600, 3, datetime.date(2012, 11, 13), 1, 0.926, '2XjrkKR1HR1ih8mj4O731z', 2436, 'Guided By Voices', None, 71728, 'The Bears for Lunch', '0V92sostdRqcKmITyxDayM'),
            #   (836752, 'Too Tired to Cry', 157893, 1, datetime.date(2013, 7, 4), 1, 0.425, '1EnaaEIrf0Vpd6udwfLhsy', 240762, 'Josh Blakesley', "'2CUhUJmoFQQBMdtFVyfJsy'", 22849, 'Waiting', '0W9qCb5BsEOZvxiRWM4l8D'),
            #   (771131, 'Rakkauden ranta', 174667, 3, datetime.date(2004, 4, 22), 0, 0.67, '0nHWTYeSobloI5CCTXgaP2', 155374, 'Topi Sorsakoski', "'2E5oIWJKpGAckSxFSRpcE6'", 33750, 'Unohtumattomat 2', '53c71wbQjzrLisfRGtzTSW'),
            #   (481473, 'No Life', 137267, 12, datetime.date(2009, 3, 17), 0, 0.785, '4mwloGvQdcH0rp9CZp77M3', 166103, 'DD/MM/YYYY', "'6pNCIXNVRwDbHdAjryQnJu'", 39564, 'Black Square', '3m20Y2bqFDWB76Whvli0pi')],
        #   'Soul Music':
            #   [(1417160, 'Soul Fifty', 157440, 12, datetime.date(2020, 3, 11), 0, 0.92, '5jc5izQICaxeyuHpQz1hUz', 169183, 'Ilkay Sencan', "'5deLgmgAEgy8UHOfJ9Dj8w'", 97103, "Spinnin' Sessions Miami 2020", '7oRaGk7DUDdcK56fWy2R2n'),
            #   (997231, 'Transmogrify', 219267, 5, datetime.date(2017, 1, 20), 0, 0.756, '5g5Ai3iIpN70GVQ1s9KOoM', 192637, 'Jennifer Batten', "'2do23WC80xqJDtFR2aZj0k'", 19189, 'She Rocks, Vol. 1', '0TaFi276OGFbguqOjk7wO4'),
            #   (778733, 'Why Baby Why', 144760, 9, datetime.date(1987, 1, 1), 1, 0.471, '7le9La5WJksGFxbeQGqmPo', 3424, 'Wild Cherry', None, 15620, 'Super Hits', '1eYIyYvmzOeqgOi05hRozA'),
            #   (962670, 'Sails Of Galway', 285920, 10, datetime.date(1997, 8, 12), 0, 0.267, '1cQr8sra4mQJs3AjyV5rOt', 153138, 'Nightnoise', "'6rAhrNLT74fBi4zb16RVf8'", 23321, 'Celtic Christmas III', '6VHsWgXJqepgq55m6sQxEY'),
            #   (891604, 'Village of Whispers', 436000, 2, datetime.date(2015, 8, 4), 0, 0.959, '0OGQf5r0TeE6ERhrhrqi4p', 158546, 'LittleVMills', "'0g46NLs3BOlUsVgCpejZpZ'", 131424, 'Killer Instinct (Original Game Soundtrack), Season 2', '2XQNpQhzOvPagQ8wGuUfqS'),
            #   (586683, 'Meditaçao', 405360, 3, datetime.date(2013, 11, 26), 0, 0.465, '6u8Rlns2AOOuGvq9CdMq3s', 240568, 'Joan Chamorro', "'0DuHQPF3vijiN2raRXwx2c'", 84003, 'Live at Jamboree - Barcelona', '7tXiRWUOJWPqTxFIjbpvue'),
            #   (1125567, 'Blitzkrieg Bop (Single Version)', 132080, 10, datetime.date(2019, 3, 29), 1, 0.697, '3myUqFk9yyxjuzsGbCes8P', 182278, 'Noel Harrison', "'4bcKtHlKBhkEXB1cVY5Ull'", 111380, 'Absolute Cinema', '2M3iYeshEYzQjlYx8gun7D'),
            #   (1203814, "It's Begining To Look A Lot Like Christmas/We Need A Little Chr", 140227, 6, datetime.date(2005, 1, 1), 1, 0.377, '0eVgn7Jug5ysAuCE1sa0MT', 573, 'Luther Vandross', None, 76146, 'This Is Christmas', '5xwoJ2MxJc7XDm5igZ0nNQ'),
            #   (1379041, 'Petites Victoires', 207000, 5, datetime.date(2019, 7, 1), 1, 0.354, '7tKGHM4k3vPMb1OBUfW9Jo', 248734, 'Léman', "'2EnOL1ADehfBQB03ELa3QQ'", 95808, 'Un jour pour une musique vol.1', '6HstWSxRZlNTMwQw2UC7r9'),
            #   (467957, 'Free Ride', 187667, 10, datetime.date(2009, 1, 16), 1, 0.719, '1qpDXk1kD6z5zKqthbTh2d', 3424, 'Wild Cherry', None, 61313, 'Hits Of The 70s (100 Songs)', '6gpQC2uJRJGThhD3rzWXTS')],
            #   'Pop/Rock': [(1110820, "I Can't Stand the Rain - Remix '94", 174133, 2, datetime.date(2007, 3, 1), 1, 0.842, '0Rs9WgBlT3WQvNhveYsKDs', 1509, 'Five', None, 14491, 'Greatest Hits', '5dXjkwmrW65p0jUXAoQ8kU'),
            #   (1443735, 'Circadian', 203077, 11, datetime.date(2019, 2, 3), 1, 0.575, '1gCbqAFwRINsRjCiDA7NSW', 257157, 'dir-s', "'1ijiF9SQEN8AlGb3VCYR6c'", 60234, 'All Nighter, Vol. 2', '1Jz8VING3PnZFbgAGQAXgb'),
            #   (561523, 'Whispers of Wonders', 232253, 1, datetime.date(2014, 5, 6), 1, 0.505, '3b9HzJ5BwL5SEZ2owgoeT2', 269988, 'Audiomachine', "'5F4ObszoeVebqtc0B3XqJa'", 90759, 'Phenomena', '3FabeiSTmOrCJ83MRPaMrd'),
            #   (1396956, 'I.G.Y.', 363413, 9, datetime.date(2019, 9, 20), 0, 0.559, '7uhRwdhfdeuQwYXYxRjcmz', 1345, 'a-ha', None, 60542, 'Drive: Smooth Car Classics', '44TBHtVIjFuDeRYm6WiLIh'),
            #   (1064035, 'Silver Bells - with The Royal Philharmonic Orchestra', 176027, 10, datetime.date(2017, 11, 24), 1, 0.428, '2uxlvWVbCVKb8BdRwCchkf', 1695, 'Elvis Presley', None, 87208, 'Christmas with Elvis and the Royal Philharmonic Orchestra (Deluxe)', '11FCLUM5m9GiuxjGEoTVF5'),
            #   (788655, 'Smokey Mountain Rain', 267173, 8, datetime.date(2002, 9, 24), 1, 0.475, '72EVQBDAMopmRc6AiGEDQU', 2592, 'Fleetwood Mac', None, 15551, 'Live', '4UbkuAbadZkGvSsjgaDLve'),
            #   (1498940, 'Ich bin ein wahrer Satan - (Live at Wacken 2017)', 274667, 4, datetime.date(2018, 7, 20), 0, 0.921, '1ug7rfLw7gNSQf6eZeBY41', 1378, 'Rage', None, 33543, 'Live At Wacken 2017: 28 Years Louder Than Hell',
            #   '3XdOaVUr2YMaIFw8VWAik4'), (696742, '3 Gymnopedies (Arr. For Flute And Harp): Gymnopedie No. 1 (Arr. For Flute And Harp)', 180333, 8, datetime.date(2002, 2, 6), 1, 0.0626, '3FGFxUqQ0rqkGmlQnjk9ND', 152011, 'Jozsef Mukk', "'3yHNGbYpLmtM7XfOQ0UiTY'", 66436, "A Bride's Guide To Wedding Music", '4uYEGDwNQDFqNubesqZ5yH'),
            #   (1119179, 'One Voice (Acoustic)', 210985, 3, datetime.date(2016, 4, 16), 1, 0.288, '2BBSOBd2cCLF1LaBow2B5t', 282165, 'Barry Gibb', "'7Hd38PVp634oGEb9pIDs5d'", 29359, 'One Voice', '69TPOVVeA5VBEPWLrCMQ4f'),
            #   (437522, 'Wheel in the Sky', 252507, 3, datetime.date(1988, 11, 29), 0, 0.764, '5i36c6C2XRw8U71yWgcoTn', 1999, 'Bone Thugs-n-Harmony', None, 14491, 'Greatest Hits', '5dXjkwmrW65p0jUXAoQ8kU')]}
        # ...
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
    print(get_album_recommendations(10, "The Big Boss"))