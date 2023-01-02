from typing import List, Tuple
from repositories.base import BaseRepository


class ArtistAbstract:

    def to_dict(self) -> dict:
        """
        :return: Returns a dictionary representation of the object.
        """
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        return str(self.to_dict())


class Artist(ArtistAbstract):
    """
    An artist object that represents an artist in the database.
    Only has the fields that are in the songs table.
    """

    def __init__(self, artist_name, spotify_id):
        self.artist_name = artist_name
        self.spotify_id = spotify_id

    def to_dict(self):
        return {
            'artist_name': self.artist_name,
            'spotify_id': self.spotify_id,
        }

    def __eq__(self, other):
        return self.spotify_id == other.song_spotify_id


class ArtistWithRating(Artist):
    """
    An artist object that represents an artist in the database.
    Has the fields in the artist table + the rating.
    """

    def __init__(self, artist_name, spotify_id, rating):
        super().__init__(artist_name, spotify_id)
        self.rating = rating

    def to_dict(self):
        return {
            'song_name': self.artist_name,
            'song_spotify_id': self.spotify_id,
            'rating': self.rating
        }


class ArtistsRepository(BaseRepository):
    def add_artist(self, name: str, pwd: str):
        return self._execute_query("INSERT INTO artists VALUES (NULL, %s, %s, NULL)", name, pwd)

    def get_all_artists(self):
        return self._execute_query("SELECT * FROM artists")

    def get_artist_by_name(self, artist_name: str):
        return self._execute_query("SELECT * FROM artists WHERE artist_name=%s", artist_name)

    def login_artist_check(self, artist_name: str, password: str) -> bool:
        return len(self._execute_query("SELECT * FROM artists WHERE artist_name=%s AND pwd=%s",
                                       artist_name,
                                       password)) > 0

    def get_artist_albums(self, artist_id: int) -> List[str]:
        albums = self._execute_query("""
                                    Select album_name
                                    From albums
                                    Inner Join artist_album_connector as aa On aa.album_id = albums.album_id
                                    Where aa.artist_id = %s
        """, artist_id)
        return [album[0] for album in albums]

    def get_artist_albums_by_name(self, artist_name: str) -> List[Tuple]:
        return self._execute_query("""
                                SELECT * FROM albums WHERE album_id IN(
                                    SELECT album_id FROM artist_album_connector WHERE artist_id = 
                                        (SELECT artist_id FROM artists WHERE artist_name = %s))
                                    """, artist_name)

    def get_artist_avg_rating(self, artist_name: str) -> float:
        avg_rating = self._execute_query("""SELECT AVG(rating) FROM comment_on_song WHERE song_id IN
        (SELECT song_id FROM songs WHERE album IN
            (SELECT album_id FROM albums WHERE album_id IN(
                SELECT album_id FROM artist_album_connector WHERE artist_id = 
                    (SELECT artist_id FROM artists WHERE artist_name = %s))))""", artist_name)
        return avg_rating[0][0]

    def get_highest_rated_artists(self, n: int) -> List[Tuple[str, int]]:
        top_n_artists = self._execute_query("""
                                    SELECT artist_name, avg_art FROM artists JOIN
                                    (SELECT artist_id, AVG(avg_alb) AS avg_art FROM artist_album_connector AS abc JOIN(
                                    SELECT album, AVG(avg_rate) as avg_alb FROM songs JOIN
                                    (SELECT AVG(rating) as avg_rate, song_id
                                     FROM comment_on_song GROUP BY song_id) AS avg_ratings
                                     ON avg_ratings.song_id = songs.song_id GROUP BY album) AS avg_album_ratings
                                     ON avg_album_ratings.album = abc.album_id GROUP BY artist_id) AS avg_artist_rating
                                     ON artists.artist_id = avg_artist_rating.artist_id ORDER BY avg_art DESC LIMIT %s;
                                    """, n)
        return top_n_artists

    def link_artist_to_genre(self, artist_name: str, genre_name: str):
        return self._execute_query("""
                                    INSERT INTO artist_genre_connector VALUES
                                    ((SELECT artist_id FROM artists WHERE artist_name = %s),
                                    (SELECT genre_id FROM genres WHERE genre_name = %s))
                                    """, artist_name, genre_name)


if __name__ == '__main__':
    import time

    s = time.perf_counter()
    print(ArtistsRepository().get_instance().get_highest_rated_artists(n=50))
    print(time.perf_counter() - s)
