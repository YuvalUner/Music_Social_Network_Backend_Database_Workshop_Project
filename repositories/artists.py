import hashlib

from repositories.base import BaseRepository


class ArtistsRepository(BaseRepository):
    def add_artist(self, name: str, pwd: str):
        return self._execute_query("INSERT INTO artists VALUES (NULL, %s, %s, NULL)",
                                   name,
                                   hashlib.sha256(pwd.encode()).hexdigest())

    def get_all_artists(self):
        return self._execute_query("SELECT * FROM artists")

    def get_artist_by_name(self, artist_name: str):
        return self._execute_query("SELECT * FROM artists WHERE artist_name=%s", artist_name)

    def login_artist_check(self, artist_name: str, password: str) -> bool:
        return len(self._execute_query("SELECT * FROM artists WHERE artist_name=%s AND pwd=%s",
                                       artist_name,
                                       password)) > 0
