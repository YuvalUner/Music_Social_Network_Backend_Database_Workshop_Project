import string

from repositories.base import BaseRepository


class AlbumsRepository(BaseRepository):
    def get_all_albums(self):
        return self._execute_query("SELECT * FROM albums")

    def get_album_by_name(self, album_name: str):
        """
        Return album details by name.
        :param album_name: Self explanatory.
        :return: album_id, album_name, spotify_album_id, average (new feature)
        """
        # return self._execute_query("SELECT * FROM albums WHERE album_name=%s", album_name)
        query = "select album_id, album_name, album_spotify_id, avg(averages.rtg)" \
                " from albums" \
                " join" \
                " (select song_id, avg(rating) as rtg" \
                " from comment_on_song" \
                " where song_id in (select song_id from songs where album =" \
                " (select album_id from albums where album_name='{trg}')) " \
                " group by song_id) as averages" \
                " where album_name = '{trg}'" \
                " group by album_id;".format(trg=album_name)
        return self._execute_query(query)

    def add_album(self, album_name: str, album_spotify_id: str):
        return self._execute_query("INSERT INTO albums VALUES (NULL, %s, %s)", album_name, album_spotify_id)

    def get_all_albums_ratings(self):
        """
        Get all album and their rating (as avg of all ratings they got).
        :return: list of (album_id, album_name, rating)
        """
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

    def get_x_highest_ranked_albums(self, num):
        """
        Get the NUM highest ranked albums.
        :param num: num of albums.
        :return: (album_id, album_name, rating) of top NUM albums.
        """
        qur_str = "select album_id, album_name, by_id.avg_rtg" \
                  " from albums" \
                  " join (select album, avg(rtg) as avg_rtg from songs" \
                  " join (select comment_on_song.song_id as id, avg(comment_on_song.rating) as rtg" \
                  " from comment_on_song" \
                  " group by comment_on_song.song_id) as avg_per_song" \
                  " on avg_per_song.id = songs.song_id" \
                  " group by album) as by_id" \
                  " on album_id = by_id.album" \
                  " order by by_id.avg_rtg desc" \
                  " limit {l_num};".format(l_num=num)
        return self._execute_query(qur_str)


if __name__ == '__main__':
    res = AlbumsRepository.get_instance().get_album_by_name('Swim')
    print(res)
