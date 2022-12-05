from repositories.base import BaseRepository


class AlbumsRepository(BaseRepository):
    def get_all_albums(self):
        return self._execute_query("SELECT * FROM albums")

    def get_album_by_name(self, album_name: str):
        return self._execute_query("SELECT * FROM albums WHERE album_name=%s", album_name)

    def add_album(self, album_name: str, album_spotify_id: str):
        return self._execute_query("INSERT INTO albums VALUES (NULL, %s, %s)", album_name, album_spotify_id)
