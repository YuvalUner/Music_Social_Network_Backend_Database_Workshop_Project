from repositories.base import BaseRepository
from typing import List, Tuple


class CommentsRepository(BaseRepository):

    def add_comment_to_song(self, song_name: str, album_name: str, artist_name: str, comment: str, rating: int) -> None:
        """
        Adds a comment to a song.
        :param song_name: The name of the song.
        :param album_name: The name of the album.
        :param artist_name: The name of the artist.
        :param comment: The comment to add.
        :param rating: The rating of the comment.
        """
        self._execute_query("""
            INSERT INTO comment_on_song VALUES ((SELECT song_id FROM songs WHERE song_name = %s
             AND album = (SELECT album_id FROM albums WHERE album_name = %s)),
            (SELECT artist_id FROM artists WHERE artist_name = %s), %s, %s); 
        """, song_name, album_name, artist_name, comment, rating)

    def get_comments_on_song(self, song_name: str, album_name: str) -> List[Tuple]:
        """
        Gets all the comments on a song.
        :param song_name: The name of the song.
        :param album_name: The name of the album.
        :return: A list of tuples with the following info in this order:
        artist name, comment, rating.
        """
        return self._execute_query("""
            SELECT artist_name, comment_text, rating FROM artists JOIN
            (SELECT * FROM comment_on_song WHERE song_id = 
            (SELECT song_id FROM songs WHERE song_name = %s
             AND album = (SELECT album_id FROM albums WHERE album_name = %s)))
             AS co ON co.commenter_id = artists.artist_id;
        """, song_name, album_name)
