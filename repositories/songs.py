from repositories.base import BaseRepository
from typing import List, Tuple


class SongRepository(BaseRepository):

    def approx_song_search_with_artist_and_album(self, song_name: str) -> List[Tuple]:
        """
        Returns a list of songs that are similar to the song_name parameter, along with their album, artist, and
        the additional information about them.
        :param song_name: The name of the song to search for.
        :return: A list of songs that are similar to the song_name parameter, with the following info in this order:
        song name, song duration, song key, song release date, song in major or not, song energy,
        song spotify id, artist name, artist id, album id, album name.
        Each song can have more than one entry if the song is performed by more than 1 artist.
        """
        return self._execute_query("SELECT "
                                   "s.song_name, s.duration, s.song_key, s.release_date, s.is_major,"
                                   " s.energy, s.song_spotify_id, art_alb_full.ar_name AS artist_name,"
                                   " art_alb_full.al_id AS album_id, art_alb_full.album_name "
                                   "FROM songs as s JOIN "
                                   "(SELECT "
                                   "alb.album_id AS al_id, alb.album_name, alb.album_spotify_id, a_id, ar_name "
                                   "FROM albums AS alb JOIN "
                                   "(SELECT art.artist_id AS a_id, abc.album_id AS al_id, art.artist_name AS ar_name "
                                   "FROM artist_album_connector AS abc JOIN "
                                   "artists as art ON art.artist_id = abc.artist_id) "
                                   "AS art_alb ON art_alb.al_id = alb.album_id) "
                                   "AS art_alb_full "
                                   "ON s.album =  art_alb_full.al_id WHERE s.song_name LIKE CONCAT('%', %s, '%');",
                                   song_name)

    def exact_song_search_with_artist_and_album(self, song_name: str) -> List[Tuple]:
        """
        Returns a list of songs with the same name as the song name, along with their album, artist, and
        the additional information about them.
        :param song_name: The name of the song to search for.
        :return: A list of songs with the same name as the song_name parameter, with the following info in this order:
        song name, song duration, song key, song release date, song in major or not, song energy,
        song spotify id, artist name, artist id, album id, album name.
        Each song can have more than one entry if the song is performed by more than 1 artist.
        """
        return self._execute_query("SELECT "
                                   "s.song_name, s.duration, s.song_key, s.release_date, s.is_major,"
                                   " s.energy, s.song_spotify_id, art_alb_full.ar_name AS artist_name,"
                                   " art_alb_full.al_id AS album_id, art_alb_full.album_name "
                                   "FROM songs as s JOIN"
                                   "(SELECT "
                                   "alb.album_id AS al_id, alb.album_name, alb.album_spotify_id, a_id, ar_name "
                                   "FROM albums AS alb JOIN "
                                   "(SELECT art.artist_id AS a_id, abc.album_id AS al_id, art.artist_name AS ar_name "
                                   "FROM artist_album_connector AS abc JOIN "
                                   "artists as art ON art.artist_id = abc.artist_id) "
                                   "AS art_alb ON art_alb.al_id = alb.album_id) "
                                   "AS art_alb_full "
                                   "ON s.album =  art_alb_full.al_id WHERE s.song_name = %s;",
                                   song_name)

    def get_song_by_song_name_and_album_name(self, song: str, album: str) -> List[Tuple]:
        """
        Returns a single song in an album with the same name as the song name and album name.
        :param song: The name of the song.
        :param album: The name of the album.
        :return: List that contains a single tuple with the following info in this order:
        song id, song name, album id, song duration, song key, song release date, song in major or not, song energy,
        song spotify id.
        """
        return self._execute_query("SELECT * FROM songs AS s WHERE"
                                   " s.album = (SELECT album_id FROM albums WHERE album_name = %s)"
                                   " AND s.song_name = %s;", song, album)

    def get_songs_in_album(self, album: str) -> List[Tuple]:
        """
        Returns all songs in a specific album.
        :param album: The name of the album.
        :return: List of songs in the album with the following info in this order:
        song id, song name, album id, song duration, song key, song release date, song in major or not, song energy,
        song spotify id.
        """
        return self._execute_query("SELECT * FROM songs AS s WHERE "
                                   "s.album = (SELECT album_id FROM albums WHERE album_name = %s);", album)

    def get_song_rating(self, song: str, album: str) -> List[Tuple]:
        """
        Returns the rating of a song.
        :param song: The name of the song.
        :param album: The name of the album the song belongs to.
        :return: A single rating value for the song, averaged from all the ratings given to it.
        """
        return self._execute_query("SELECT AVG(rating) FROM comment_on_song "
                                   "WHERE song_id = (SELECT song_id FROM songs "
                                   "WHERE song_name = %s "
                                   "AND album = (SELECT album_id FROM albums WHERE album_name = %s));", song, album)

    def get_top_rated_songs(self, limit: int) -> List[Tuple]:
        """
        Returns the top rated songs.
        :param limit: The number of top rated songs to return.
        :return: A list of the top rated songs with the following info in this order:
        song name, album id, song duration, song key, song release date, song in major or not, song energy,
        song spotify id, rating.
        """
        return self._execute_query("SELECT songs.song_id, song_name, album, duration, song_key, release_Date, "
                                   "is_major, energy, song_spotify_id, avg_rating "
                                   "FROM songs JOIN "
                                   "(SELECT AVG(rating) as avg_rating, "
                                   "song_id FROM comment_on_song GROUP BY song_id ORDER BY avg_rating DESC LIMIT %s) "
                                   "AS rtngs "
                                   "ON songs.song_id = rtngs.song_id "
                                   "GROUP BY songs.song_id;", limit)

    def get_top_rated_songs_per_year(self, rel_date: str, lim: int) -> List[Tuple]:
        """
        Returns the top rated songs per year.
        :param rel_date: A date string containing the year the songs were released.
        :param lim: How many songs to get.
        :return: A list of the top rated songs per year with the following info in this order:
        song name, album id, song duration, song key, song release date, song in major or not, song energy,
        song spotify id, rating.
        """
        return self._execute_query("SELECT year_songs.song_id, song_name, album, duration, song_key, release_Date, "
                                   "is_major, energy, song_spotify_id, avg_rating "
                                   "FROM (SELECT * FROM songs WHERE YEAR(release_date) = "
                                   "YEAR(STR_TO_DATE(%s, '%Y-%m-%d'))) AS year_songs "
                                   "JOIN (SELECT AVG(rating) as avg_rating, song_id "
                                   "FROM comment_on_song GROUP BY song_id) "
                                   "AS rtngs "
                                   "ON year_songs.song_id = rtngs.song_id "
                                   "GROUP BY year_songs.song_id "
                                   "ORDER BY avg_rating DESC LIMIT %s;", rel_date, lim)

    def add_song(self, song_name: str, album_name: str, artist_name: str, spotify_id: str, dur: int,
                 scale: str, rel_date: str, is_major: bool, energy: float) -> None:
        """
        Adds a song to the database.
        :param song_name: the song's name.
        :param album_name: the name of the album the song belongs to.
        :param artist_name: the name of an artists related to the song.
        :param spotify_id: the spotify id of the song.
        :param dur: the song's duration in miliseconds.
        :param scale: the song's key.
        :param rel_date: the song's release date.
        :param is_major: whether the song is in major or not.
        :param energy: the song's energy.
        :return: True if the song was added successfully, False otherwise.
        """
        self._execute_query("CALL add_song(%s, %s, %s, %s, %s, %s, %s, %s, %s);", song_name, album_name,
                                artist_name, spotify_id, dur, scale, rel_date, is_major, energy)



if __name__ == '__main__':
    song_repository = SongRepository.get_instance()
    rating = song_repository.get_song_rating("Name", "Name")
    print(rating)
    top_songs = song_repository.get_top_rated_songs(10)
    print(top_songs)
    top_songs_per_year = song_repository.get_top_rated_songs_per_year("2019-01-01", 10)
    print(top_songs_per_year)
