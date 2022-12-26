from repositories.base import BaseRepository


class AlbumsRepository(BaseRepository):
    def get_all_albums(self):
        return self._execute_query("SELECT * FROM albums")

    def get_album_by_name(self, album_name: str):
        return self._execute_query("SELECT * FROM albums WHERE album_name=%s", album_name)

    def add_album(self, album_name: str, album_spotify_id: str):
        return self._execute_query("INSERT INTO albums VALUES (NULL, %s, %s)", album_name, album_spotify_id)

    def get_all_albums_ratings(self):
        return self._execute_query("select album_id, album_name, by_id.avg_rtg"
                                   " from albums"
                                   " join (select album, avg(rtg) as avg_rtg from songs"
                                   " join (select comment_on_song.song_id as id, avg(comment_on_song.rating) as rtg"
                                   " from comment_on_song"
                                   " group by comment_on_song.song_id) as avg_per_song"
                                   " on avg_per_song.id = songs.song_id"
                                   " group by album) as by_id"
                                   " on album_id = by_id.album"
                                   " order by album_id;")

"""
if __name__ == '__main__':
    ar = AlbumsRepository.get_instance()
    res = ar.get_all_albums_ratings()
    print(res)
"""