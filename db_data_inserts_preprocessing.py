import csv
import string
import time

import mysql.connector
import random

from config import consts


def timed(f):
    '''decorator for printing the timing of functions
    usage:
    Stolen right from Artificial Intelligence ex 1.
    @timed
    def some_funcion(args...):'''

    def wrap(*x, **d):
        start = time.perf_counter()
        res = f(*x, **d)
        print(f.__name__, ':', time.perf_counter() - start)
        return res

    return wrap


def gen_rand_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


@timed
def read_csv(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)


def connect():
    return mysql.connector.connect(
        host=consts.DB_HOST,
        user=consts.DB_USER,
        password=consts.DB_PASSWORD,
        database=consts.DB_NAME,)


class ArtistDataMethods:
    """
    A collection of methods for the artist-data.csv file.
    Generally, what the methods do is all in their names.
    To use for each type of data, run the "get" method, then the "add" or "link" method for that data.
    """

    def __init__(self):
        self.connection = connect()
        self.cursor = self.connection.cursor()

    def finish_connection(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    @staticmethod
    def collect_genres_set(genres):
        genres_set = set()
        for genre in genres:
            genre = genre.split(';')
            for g in genre:
                genres_set.add(g.strip())
        return genres_set

    @staticmethod
    def collect_artists_set(artists):
        artists_set = set()
        for artist in artists:
            artists_set.add(artist)
        return artists_set

    def add_genres(self, genres):
        for genre in genres:
            self.cursor.execute("CALL add_genre(%s)", (genre,))
        self.connection.commit()

    def add_artists(self, artists):
        for artist in artists:
            pwd = gen_rand_string(8)
            self.cursor.execute("CALL add_artist(%s, %s, %s)", (artist, pwd, ''))
        self.connection.commit()

    @staticmethod
    def get_artist_genre_connections(csv_data):
        artist_genre_tuples = []
        for row in csv_data:
            artist = row[0]
            genres = row[1].split(';')
            for genre in genres:
                artist_genre_tuples.append((artist, genre.strip()))
        return artist_genre_tuples

    # If executing, execute this last from this class.
    def link_artist_to_genres(self, artist_genres_tuples):
        for artist, genre in artist_genres_tuples:
            self.cursor.execute("CALL link_artist_to_genre(%s, %s)", (artist, genre,))
        self.connection.commit()


def split(a, n):
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


class Song:

    def __init__(self, song_id, song_name, album, artist, date, duration, is_major, energy, key):
        self.song_id = song_id
        self.song_name = song_name
        self.album = album
        self.date = date
        self.duration = duration
        self.is_major = is_major
        self.energy = energy
        self.key = key
        # This value is only in case there is no album - which should never happen, but just in case.
        self.artist = artist


class TrackFeaturesMethods:
    """
    A collection of methods for the track-features.csv file.
    Generally, what the methods do is all in their names.
    To use for each type of data, run the "get" method, then the "add" or "link" method for that data.
    """

    def __init__(self):
        self.connection = connect()
        self.cursor = self.connection.cursor()
        self.data = dict()

    def finish_connection(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    @timed
    def collect_artist_and_spotify_ids(self, csv_data):
        artist_spotify_id_tuples = set()
        row_num = 0
        for row in csv_data:
            artists = row[4].replace('[', '').replace(']', '').split(',')
            spotify_ids = row[5].replace('[', '').replace(']', '').split(',')
            for index, artist in enumerate(artists):
                artist = artist.strip().replace("'", "")
                try:
                    artist_spotify_id_tuples.add((artist, spotify_ids[index].strip()))
                # If an artist has no spotify id, give them an empty string as their spotify id.
                except IndexError:
                    artist_spotify_id_tuples.add((artist, ''))
            print(f"Row {row_num} processed.")
            row_num += 1
        self.data['artist_spotify_id_tuples'] = artist_spotify_id_tuples

    # Run this after collect_artist_and_spotify_ids
    @timed
    def add_artists(self):
        row_num = 0
        for artist, spotify_id in self.data['artist_spotify_id_tuples']:
            try:
                pwd = gen_rand_string(8)
                self.cursor.execute("CALL add_artist(%s, %s, %s)", (artist, pwd, spotify_id))
                print(f"Row {row_num} processed.")
            except mysql.connector.errors.IntegrityError:
                pass
            row_num += 1
        self.connection.commit()

    @timed
    def collect_albums_and_spotify_ids(self, csv_data):
        album_spotify_id_tuples = set()
        row_num = 0
        for row in csv_data:
            album = row[2].strip()
            album_spotify_id_tuples.add((album, row[3].strip()))
            print(f"Row {row_num} processed.")
            row_num += 1
        self.data['album_spotify_id_tuples'] = album_spotify_id_tuples

    # Run this after collect_albums_and_spotify_ids
    @timed
    def add_albums(self):
        row_num = 0
        for album, album_id in self.data['album_spotify_id_tuples']:
            try:
                self.cursor.execute("CALL add_album(%s, %s)", (album, album_id))
                print(f"Row {row_num} processed.")
            # There are duplicate album names in the dataset, so we ignore them.
            # This does cause some albums to not be added, but it's not a big deal.
            # At worst, some songs will be associated to the wrong artists.
            except mysql.connector.errors.IntegrityError:
                pass
            row_num += 1
        self.connection.commit()

    @timed
    def collect_artist_and_album_connections(self, csv_data):
        artist_album_tuples = set()
        row_num = 0
        for row in csv_data:
            artists = row[4].replace('[', '').replace(']', '').split(',')
            album = row[2].strip()
            for artist in artists:
                artist_album_tuples.add((artist.strip().replace("'", ""), album))
            print(f"Row {row_num} processed.")
            row_num += 1
        self.data['artist_album_tuples'] = artist_album_tuples

    # Run this after collect_artist_and_album_connections
    # Must be run async because it takes a long time. Like 10 hours long.
    def link_artists_to_albums(self):
        row_num = 0
        current = 0
        batch = 0
        artist_album_tuples = list(self.data['artist_album_tuples'])
        total = len(artist_album_tuples)
        print(total)
        # for artist_album_tuple in artist_album_tuples:
        #     try:
        #         self.cursor.executemany("CALL link_artist_to_album(%s, %s)", artist_album_tuple)
        #         self.connection.commit()
        #         print(f"Batch {batch} / 30000 processed.")
        #         batch += 1
        #     except:
        #         print(f"Error on batch {batch} / 30000.")
        for artist, album in artist_album_tuples:
            try:
                self.cursor.execute("CALL link_artist_to_album(%s, %s)", (artist, album,))
                row_num += 1
                current += 1
                if current == 1000:
                    print(f"Row {row_num} / {total} processed.")
                    self.connection.commit()
                    current = 0
            # Ignore any odd data that can cause errors. There should not be any, but still.
            except:
                pass
        self.connection.commit()

    @timed
    def add_keys(self):
        key_list = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        for key in key_list:
            self.cursor.execute("CALL add_scale(%s)", (key,))
        self.connection.commit()

    @staticmethod
    def map_index_to_key(key_index):
        key_list = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return key_list[key_index]

    @timed
    def collect_track_features(self, csv_data):
        songs = []
        row_num = 0
        for row in csv_data:
            song_id = row[0].strip()
            song_name = row[1].strip()
            album = row[2].strip()
            date = row[23].strip()
            artists = row[4].replace('[', '').replace(']', '').split(',')
            artist = artists[0].strip()
            # Handle cases where the date is incomplete or unknown by going with the "eh, close enough" approach.
            if date == '':
                # If no date is given (or the song was performed by Jesus), just use this nonsense date.
                date = "0001-01-01"
            if len(date) == 4:
                date += "-01-01"
            elif len(date) == 7:
                date += "-01"
            duration = row[20].strip()
            is_major = int(row[13].strip())
            energy = row[10].strip()
            key = TrackFeaturesMethods.map_index_to_key(int(row[11].strip()))
            songs.append(Song(song_id, song_name, album, artist, date, duration, is_major, energy, key))
            print(f"Row {row_num} processed.")
            row_num += 1
        self.data['songs'] = songs

    # Run this after collect_track_features
    @timed
    def add_songs(self):
        row_num = 0
        for song in self.data['songs']:
            try:
                self.cursor.execute("CALL add_song(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                    (song.song_name, song.album, '', song.song_id, song.duration, song.key,
                                     song.date, song.is_major, song.energy))
            # Very unlikely to happen, but if 2 songs with the same album exist, we ignore the second one.
            # Also, for some reason, 1 specific song causes a "data truncated" error, so we ignore that one too.
            # We have enough data to work with, so it's not a big deal.
            except:
                pass
            print(f"Row {row_num} processed.")
            row_num += 1
        self.connection.commit()


class GeneratedDataAdder:
    """
    This class is used to add data to the database that is not in the original dataset.
    It generates the data then adds it to the database.
    """

    def __init__(self):
        self.connection = connect()
        self.cursor = self.connection.cursor()
        # Hard coded the values because this should only be executed once, ever.
        self.min_song_id = 348602
        self.max_song_id = 1552596
        self.min_artist_id = 146790
        self.max_artist_id = 289347

    def finish_connection(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def generate_and_add_comments(self, count):
        """
        Generates and adds comments to the database.
        :param count:
        :return:
        """
        great_comments = ["Great song!", "I love this song!", "This song is amazing!", "This song is so good!",
                          "This song is so catchy!", "This song is so fun!", "This song is so groovy!", ]
        good_comments = ["This song is good!", "This song is alright.", "This song is pretty good.",
                         "This song is decent.",
                         "This song is okay.", "This song is not bad.", "This song is not too bad."]
        bad_comments = ["This song is bad.", "This song is not good.", "This song is not very good.",
                        "This song is not too good.",
                        "This song is awful.", "I hate this song!", "This song is terrible!", "This song is so bad!"]

        for i in range(count):
            comment = ""
            rating = random.randint(1, 5)
            if rating == 5:
                comment = random.choice(great_comments)
            elif rating == 4 or rating == 3:
                comment = random.choice(good_comments)
            else:
                comment = random.choice(bad_comments)
            song_id = random.randint(self.min_song_id, self.max_song_id)
            user_id = random.randint(self.min_artist_id, self.max_artist_id)
            try:
                self.cursor.execute("CALL add_comment_by_ids(%s, %s, %s, %s)", (song_id, user_id, comment, rating))
            # Not impossible to add duplicates which will violate PK constraints, so we ignore them.
            except:
                pass
        self.connection.commit()

    def generate_and_add_favorite_songs(self, count):
        """
        Generates and adds favorite songs to the database.
        :param count:
        :return:
        """
        for i in range(count):
            song_id = random.randint(self.min_song_id, self.max_song_id)
            user_id = random.randint(self.min_artist_id, self.max_artist_id)
            try:
                self.cursor.execute("CALL add_favorite_song_by_ids(%s, %s)", (song_id, user_id))
            # Not impossible to add duplicates which will violate PK constraints, so we ignore them.
            except:
                pass
        self.connection.commit()

    def add_random_links(self):
        """
        This method adds random links between artists and genres to the database.
        :return:
        """
        genres_start = 2
        genres_end = 81
        for i in range(self.min_artist_id, self.max_artist_id):
            rand_genre = random.randint(genres_start, genres_end)
            try:
                self.cursor.execute("INSERT INTO artist_genre_connector (artist_id, genre_id) VALUES (%s, %s)",
                               (i, rand_genre))
            except:
                pass
        self.connection.commit()


if __name__ == '__main__':
    csv_data = read_csv("artists-data.csv")

    artist_data_methods = ArtistDataMethods()
    # Process all the data in the artists-data.csv file.
    # Collect and add genres
    genres = artist_data_methods.collect_genres_set(csv_data)
    artist_data_methods.add_genres(genres)
    # Collect and add artists
    artists = artist_data_methods.collect_artists_set(csv_data)
    artist_data_methods.add_artists(artists)
    # Link artists to genres
    connections = artist_data_methods.get_artist_genre_connections(csv_data)
    artist_data_methods.link_artist_to_genres(connections)
    artist_data_methods.finish_connection()

    track_features_methods = TrackFeaturesMethods()
    # Process all the data in the track-features.csv file.
    csv_data = read_csv("track-features.csv")
    # Collect artists and add them
    track_features_methods.collect_artist_and_spotify_ids(csv_data)
    track_features_methods.add_artists()
    # Collect albums and add them
    track_features_methods.collect_albums_and_spotify_ids(csv_data)
    track_features_methods.add_albums()
    # Collect connections between artists and albums and add them
    track_features_methods.collect_artist_and_album_connections(csv_data)
    track_features_methods.link_artists_to_albums()
    # Add song keys to database
    track_features_methods.add_keys()
    # Collect songs and add them
    track_features_methods.collect_track_features(csv_data)
    track_features_methods.add_songs()
    track_features_methods.finish_connection()

    # Add generated data to the database
    generated_data_adder = GeneratedDataAdder()
    # Add comments
    generated_data_adder.generate_and_add_comments(1000000)
    # Add favorite songs
    generated_data_adder.generate_and_add_favorite_songs(1000000)
    # Add random links between artists and genres
    generated_data_adder.add_random_links()





