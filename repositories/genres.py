from repositories.base import BaseRepository


class GenresRepository(BaseRepository):

    def get_all(self):
        return self._execute_query("SELECT * FROM genres")
