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
        return self._execute_query("SELECT"
                                   "s.song_name, s.duration, s.song_key, s.release_date, s.is_major,"
                                   " s.energy, s.song_spotify_id, art_alb_full.ar_name AS artist_name,"
                                   " art_alb_full.al_id AS album_id, art_alb_full.album_name"
                                   "FROM songs as s JOIN"
                                   "(SELECT"
                                   "alb.album_id AS al_id, alb.album_name, alb.album_spotify_id, a_id, ar_name"
                                   "FROM albums AS alb JOIN"
                                   "(SELECT art.artist_id AS a_id, abc.album_id AS al_id, art.artist_name AS ar_name"
                                   "FROM artist_album_connector AS abc JOIN"
                                   "artists as art ON art.artist_id = abc.artist_id)"
                                   "AS art_alb ON art_alb.al_id = alb.album_id)"
                                   "AS art_alb_full"
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
        return self._execute_query("SELECT"
                                   "s.song_name, s.duration, s.song_key, s.release_date, s.is_major,"
                                   " s.energy, s.song_spotify_id, art_alb_full.ar_name AS artist_name,"
                                   " art_alb_full.al_id AS album_id, art_alb_full.album_name"
                                   "FROM songs as s JOIN"
                                   "(SELECT"
                                   "alb.album_id AS al_id, alb.album_name, alb.album_spotify_id, a_id, ar_name"
                                   "FROM albums AS alb JOIN"
                                   "(SELECT art.artist_id AS a_id, abc.album_id AS al_id, art.artist_name AS ar_name"
                                   "FROM artist_album_connector AS abc JOIN"
                                   "artists as art ON art.artist_id = abc.artist_id)"
                                   "AS art_alb ON art_alb.al_id = alb.album_id)"
                                   "AS art_alb_full"
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
        return self._execute_query("SELECT * FROM songs AS s WHERE "
                                   "s.album = (SELECT album_id FROM albums WHERE album_name = %s)"
                                   " AND s.song_name = %s;", song, album)

    def get_songs_in_album(self, album: str) -> List[Tuple]:
        """
        Returns all songs in a specific album.
        :param album: The name of the album.
        :return: List of songs in the album with the following info in this order:
        song id, song name, album id, song duration, song key, song release date, song in major or not, song energy,
        song spotify id.
        """
        return self._execute_query("SELECT * FROM songs AS s WHERE"
                                   "s.album = (SELECT album_id FROM albums WHERE album_name = album);", album)


