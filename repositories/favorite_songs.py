from repositories.base import BaseRepository
from typing import List, Tuple


class FavoriteSongsRepository(BaseRepository):

    def add_favorite_song(self, song_name: str, album_name: str, artist_name: str) -> None:
        """
        Adds a song to the user's favorite songs.
        :param song_name: The name of the song.
        :param album_name: The name of the album.
        :param artist_name: The name of the artist.
        """
        self._execute_query("""
            INSERT INTO favorite_songs VALUES((SELECT song_id FROM songs WHERE song_name = %s AND album = 
            (SELECT album_id FROM albums WHERE album_name = %s)),
            (SELECT artist_id FROM artists WHERE artist_name = %s));
        """, song_name, album_name, artist_name)

    def get_favorite_songs(self, artist_name: str) -> List[Tuple]:
        """
        Gets all the songs the user liked.
        :param artist_name: the name of the user.
        :return: A list of tuples containing the following information, in this order:
        artist name, artist spotify id, album name, album spotify id, song name, song duration, song key,
        song release date, song in major or not, song energy, song spotify id
        """
        return self._execute_query("""
        SELECT artist_name, artist_spotify_id, album_name, album_spotify_id,
        song_name, duration, song_key, release_date, is_major, energy, song_spotify_id
        FROM artists AS a JOIN(
        SELECT artist_id, album_name, album_spotify_id, song_id, song_name, album, duration, song_key,
         release_date, is_major ,energy, song_spotify_id FROM artist_album_connector AS abc JOIN(
        SELECT * FROM albums JOIN (
        SELECT * FROM songs WHERE song_id IN
         (SELECT song_id FROM favorite_songs WHERE artist_id = 
            (SELECT artist_id FROM artists WHERE artist_name = %s))) AS ufs
            ON albums.album_id = ufs.album) AS alb ON abc.album_id = alb.album_id)
            as aac
            ON aac.artist_id = a.artist_id;""", artist_name)
