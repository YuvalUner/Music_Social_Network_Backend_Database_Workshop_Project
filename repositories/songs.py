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
        song spotify id, artist name, album id, album name.
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
        song spotify id, artist name, album id, album name.
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
                                   " AND s.song_name = %s;", album, song)

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
        artist name, album name, song name, song duration, song key, song release date, song in major or not,
        song energy, song spotify id, rating.
        """
        return self._execute_query("""
            SELECT artist_name, album_name, song_name, duration, song_key, release_date, is_major, energy,
             song_spotify_id, avg_rating FROM artists JOIN 
            (SELECT artist_id, abc.album_id, album_name, song_id, song_name, duration, song_key, release_date, is_major,
             energy, song_spotify_id, avg_rating FROM artist_album_connector AS abc JOIN
            (SELECT * FROM albums JOIN(
            SELECT songs.song_id, song_name, album, duration, song_key, release_Date, is_major, energy, song_spotify_id,
             avg_rating
            FROM songs JOIN
                (SELECT AVG(rating) as avg_rating, song_id FROM comment_on_song GROUP BY song_id ORDER BY avg_rating
                 DESC LIMIT %s)
            AS rtngs 
            ON songs.song_id = rtngs.song_id
            GROUP BY songs.song_id) AS best_songs ON albums.album_id = best_songs.album)
            AS bs_albums ON abc.album_id = bs_albums.album_id) AS bsa_artists ON bsa_artists.artist_id = artists.artist_id;
        """, limit)

    def get_top_rated_songs_per_year(self, rel_date: str, lim: int) -> List[Tuple]:
        """
        Returns the top rated songs per year.
        :param rel_date: A date string containing the year the songs were released.
        :param lim: How many songs to get.
        :return: A list of the top rated songs per year with the following info in this order:
        artist name, album name, song name, song duration, song key, song release date, song in major or not,
        song energy, song spotify id, rating.
        """
        return self._execute_query("""
        SELECT artist_name, album_name, song_name, duration, song_key, release_date, is_major, energy,
         song_spotify_id, avg_rating FROM artists JOIN(
        SELECT artist_id, abc.album_id, album_name, song_id, song_name, duration, song_key, release_date,
         is_major, energy, song_spotify_id, avg_rating  FROM artist_album_connector AS abc JOIN
        (SELECT * FROM albums JOIN(
        SELECT year_songs.song_id, song_name, album, duration, song_key, release_Date, is_major, energy,
         song_spotify_id, avg_rating
        FROM (SELECT * FROM songs WHERE YEAR(release_date) = YEAR(STR_TO_DATE(%s, "%Y-%m-%d"))) AS year_songs
        JOIN (SELECT AVG(rating) as avg_rating, song_id FROM comment_on_song GROUP BY song_id)
        AS rtngs 
        ON year_songs.song_id = rtngs.song_id
        GROUP BY year_songs.song_id
        ORDER BY avg_rating DESC
        LIMIT %s) AS top ON albums.album_id = top.album) AS top_with_albums ON top_with_albums.album_id = abc.album_id)
        AS top_with_artist_ids ON top_with_artist_ids.artist_id = artists.artist_id;
        """, rel_date, lim)

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

    def get_max_and_min_song_years(self) -> Tuple:
        """
        Returns the max and min year of songs in the database.
        :return: A list containing a single tuple with the max and min year of songs in the database.
        """
        return self._execute_query("SELECT MAX(YEAR(release_date)) AS latest_song_date,"
                                   " MIN(YEAR(release_date)) AS oldest_song_date FROM songs;")[0]

    def get_random(self, limit: int) -> List[Tuple]:
        return self._execute_query("""
        SELECT artist_name, album_name, song_name, duration, song_key, release_date, is_major, energy, song_spotify_id
        FROM artists JOIN(
        SELECT artist_id, album_name, song_name, duration, song_key, release_date, is_major, energy, song_spotify_id
         FROM artist_album_connector AS abc JOIN
        (SELECT * FROM albums JOIN
        (SELECT * FROM songs ORDER BY RAND() LIMIT %s) AS s ON albums.album_id = s.album) AS a
        ON abc.album_id = a.album_id) AS a_id ON a_id.artist_id = artists.artist_id;
        """, limit)


if __name__ == '__main__':
    pass
