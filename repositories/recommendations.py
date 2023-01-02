import random
import time

from repositories.base import BaseRepository
from typing import List, Tuple


class RecommendationsDataProcessing:

    @staticmethod
    def get_best_genres(recommendation_info: List[Tuple], count: int) -> dict:
        """
        Returns a dictionary of the best genres for the user, along a rating for each genre.
        :param recommendation_info: A list of tuples, each tuple contains the following information:
        song name, song duration, song key, song release date, song in major or not, song energy,
        song spotify id, artist name, album id, album name, artist id, artist spotify id, artist genres.
        :param count: The number of genres to return.
        :return: A dictionary of the best genres for the user, along with the total rating of that genre.
        """
        genres = {}
        for song in recommendation_info:
            genre = song[0]
            rating = song[12]
            if genre in genres:
                genres[genre] += rating
            else:
                genres[genre] = rating
        sorted_genres = {k: v for k, v in sorted(genres.items(), key=lambda item: item[1], reverse=True)}
        if len(sorted_genres) > count:
            return dict(list(sorted_genres.items())[:count])
        return sorted_genres


class RecommendationsRepository(BaseRepository):

    def get_recommendation_info_by_liked_songs(self, username: str) -> List[Tuple]:
        """
        Gets all the info needed to recommend songs, albums and artists to the user based on the songs the user liked.
        :param username: The username of the user.
        :return: A list of tuples with the following info in this order:
        genre name, artist name, artist_spotify_id, album name, album spotify id, song name, song duration,
        song key, song release date, song in major or not, song energy, song spotify id, song rating according to user.
        """
        return self._execute_query("SELECT genre_name, artist_name, artist_spotify_id, album_name, album_spotify_id, "
                                   "song_name, duration, song_key, release_date, is_major, energy, "
                                   "song_spotify_id, rating "
                                   "FROM genres JOIN( "
                                   "SELECT agc.genre_id, artist_name, artist_spotify_id, album_name, album_spotify_id, "
                                   "song_name, duration, song_key, release_date, is_major, energy, song_spotify_id, "
                                   "rating FROM artist_genre_connector as agc JOIN( "
                                   "SELECT artists.artist_id, artist_name, artist_spotify_id, album_id, album_name, "
                                   "album_spotify_id,  song_id, song_name, duration, song_key, release_date, is_major, "
                                   "energy, song_spotify_id, rating "
                                   "FROM artists JOIN( "
                                   "SELECT abc.artist_id, abc.album_id, album_name, album_spotify_id, song_id, "
                                   "song_name, duration, song_key, release_date, is_major, energy, song_spotify_id, "
                                   "rating FROM artist_album_connector AS abc JOIN "
                                   "(SELECT album_id, album_name, album_spotify_id, song_id, song_name, duration, "
                                   "song_key, release_date, is_major, energy, song_spotify_id, rating "
                                   "FROM albums AS a JOIN "
                                   "(SELECT s.song_id, song_name, album, duration, song_key, release_Date, is_major, "
                                   "energy, song_spotify_id, likely_songs.rating "
                                   "FROM songs AS s JOIN "
                                   "((SELECT song_id, rating FROM comment_on_song WHERE commenter_id = "
                                   "(SELECT artists.artist_id FROM artists WHERE artist_name = %s) "
                                   "AND rating > 3) UNION "
                                   "(SELECT song_id, 5 AS rating FROM favorite_songs WHERE artist_id "
                                   "= (SELECT artists.artist_id FROM artists WHERE artist_name = %s))) "
                                   "AS likely_songs ON s.song_id = likely_songs.song_id) AS likely_songs_info "
                                   "ON likely_songs_info.album = a.album_id) AS likely_albums ON "
                                   "abc.album_id = likely_albums.album_id) "
                                   "AS likely_artists ON likely_artists.artist_id = artists.artist_id) "
                                   "AS artist_info ON artist_info.artist_id = agc.artist_id) "
                                   "AS genres_info ON genres.genre_id = genres_info.genre_id;", username, username)

    def get_recommendations_by_liked_genres(self, genres: List, limit: int) -> dict:
        """
        Gets recommendations on albums, songs and artists via the user's liked genres.
        :param genres: A dict containing the user's preferred genres and the rating of each genre.
        :param limit: The number of recommendations to return.
        :return: A list of tuples containing the following information, in this order:
        song id, song name, song duration, song key, song release date, song in major or not, song energy,
        song spotify id, artist id, artist name, artist spotify id, album id, album name, album spotify id.
        """
        results_dict = {}
        for genre in genres:
            results_dict[genre] = self._execute_query("SELECT song_id, song_name, duration, song_key, release_date, "
                                                      " is_major, energy, song_spotify_id, "
                                                      "genre_artists_albums.artist_id, "
                                                      "genre_artists_albums.artist_name, "
                                                      "genre_artists_albums.artist_spotify_id, "
                                                      "genre_artists_albums.album_id, genre_artists_albums.album_name, "
                                                      "genre_artists_albums.album_spotify_id "
                                                      " FROM songs JOIN "
                                                      "(SELECT artist_id, artist_name, artist_spotify_id, "
                                                      "albums.album_id, album_name, album_spotify_id FROM albums JOIN( "
                                                      "(SELECT abc.artist_id, artist_name, artist_spotify_id, album_id "
                                                      "FROM artist_album_connector AS abc JOIN "
                                                      "(SELECT artists.artist_id, artist_name, artist_spotify_id FROM "
                                                      "artists WHERE artist_id IN( "
                                                      "SELECT artist_id FROM artist_genre_connector WHERE genre_id = "
                                                      "(SELECT genre_id FROM genres WHERE genre_name = %s))) "
                                                      "AS genre_artists ON "
                                                      "abc.artist_id = genre_artists.artist_id)) AS gab_nfull "
                                                      "ON gab_nfull.album_id = albums.album_id) AS "
                                                      "genre_artists_albums "
                                                      "ON songs.album = genre_artists_albums.album_id "
                                                      "ORDER BY RAND() LIMIT %s", genre, limit)
        return results_dict


if __name__ == '__main__':
    song_repository = RecommendationsRepository.get_instance()
    song = song_repository.get_recommendation_info_by_liked_songs("Glaiza De Castro")
    # print(f"Index: 0, Genre: {song[0]})")
    # print(f"Index: 1, Artist: {song[1]})")
    # print(f"Index: 2, Artist Spotify ID: {song[2]})")
    # print(f"Index: 3, Album: {song[3]})")
    # print(f"Index: 4, Album Spotify ID: {song[4]})")
    # print(f"Index: 5, Song: {song[5]})")
    # print(f"Index: 6, Duration: {song[6]})")
    # print(f"Index: 7, Key: {song[7]})")
    # print(f"Index: 8, Release Date: {song[8]})")
    # print(f"Index: 9, Is Major: {song[9]})")
    # print(f"Index: 10, Energy: {song[10]})")
    # print(f"Index: 11, Song Spotify ID: {song[11]})")
    # print(f"Index: 12, Rating: {song[12]})")
    results = RecommendationsDataProcessing.get_best_genres(song, 3)
    print(results)
    # recommendations = song_repository.get_recommendations_by_liked_genres(results, 3)
    # print(recommendations)
