from typing import List, Tuple

from repositories.base import BaseRepository


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


if __name__ == '__main__':
    import time

    s = time.perf_counter()
    print(ArtistsRepository().get_instance().get_highest_rated_artists(n=50))
    print(time.perf_counter() - s)
