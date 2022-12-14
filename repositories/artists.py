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
                                        Select res.artist_name, avg(res.rating) as top_rated from 
                                            (Select art.artist_name, comment_on_song.rating                                                                  
                                            From comment_on_song                                                      
                                            LEFT Join songs as s On s.song_id = comment_on_song.song_id              
                                            LEFT Join albums as a On a.album_id = s.album                           
                                            LEFT Join artist_album_connector as aa On a.album_id = aa.album_id       
                                            LEFT Join artists as art On aa.artist_id = art.artist_id) as res
                                            group by res.artist_name order by top_rated DESC LIMIT %s
                                        """, n)
        return top_n_artists


if __name__ == '__main__':
    import time

    s = time.perf_counter()
    print(ArtistsRepository().get_instance().get_highest_rated_artists(n=50))
    print(time.perf_counter() - s)
