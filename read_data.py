import csv
import datetime
import json
import os
from pprint import pprint
import spotipy
from pathlib import Path
from dataclasses import dataclass

SPOTIFY_API_PUBLIC = os.environ.get('SPOTIFY_API_PUBLIC')
SPOTIFY_API_PRIVATE = os.environ.get('SPOTIFY_API_PRIVATE')
SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USERNAME')
SPOTIFY_REDIRECT_URL = os.environ.get('SPOTIFY_REDIRECT_URL')
SPOTIFY_SCOPE = 'user-read-recently-played'

"""
DATA CLASSES
"""
@dataclass
class Weight:
    timestamp: int
    weight: float

@dataclass
class SleepScore:
    timestamp: int
    overall_score: int
    composition_score: int
    revitalization_score: int
    duration_score: int
    deep_sleep_in_minutes: int
    resting_heart_rate: int
    restlessness: float

    @staticmethod
    def from_dict(d):
        return SleepScore(
            timestamp=datetime.datetime.strptime(
                d['timestamp'],
                "%Y-%m-%dT%H:%M:%SZ"
            ).timestamp(),
            overall_score=int(d['overall_score']),
            composition_score=int(d['composition_score']),
            revitalization_score=int(d['revitalization_score']),
            duration_score=int(d['duration_score']),
            deep_sleep_in_minutes=int(d['deep_sleep_in_minutes']),
            resting_heart_rate=int(d['resting_heart_rate']),
            restlessness=float(d['restlessness']),
        )

@dataclass
class HeartRateReading:
    timestamp: int
    bpm: int

"""
UTIL FUNCTIONS
"""

def extract_timestamp(date, time):
    """
    Returns the timestamp (epoch time) from a given date string (MM/DD/YY) and
    time string (HH:mm:ss)
    """
    month, day, year = [int(d) for d in date.split("/")]
    h, m, s = [int(t) for t in time.split(":")]
    return datetime.datetime(2000 + year, month, day, h, m, s).timestamp()

"""
READERS
"""
class Reader:
    @classmethod
    def read_data(cls, filenames):
        def open_file(path):
            with path.open() as f:
                return json.load(f)

        files = sorted(Path().glob(filenames))
        return [
            datum
            for file in files
            for datum in open_file(file)
        ]

    @classmethod
    def get_data(cls):
        raise NotImplementedError

class SpotifyReader(Reader):
    @classmethod
    def get_data(cls):
        streamed_songs = cls.read_data('data/spotify/StreamingHistory*.json')
        token = cls._get_token()

        streamed_ids = [
            cls._search_for_song(song['trackName'], song['artistName'], token)
            for song in streamed_songs
        ]
        streamed_features = [
            info
            for i in range(0, len(streamed_ids), 50)
            for info in cls._get_song_info(streamed_ids[i:i+50], token)
        ]

        for i, feature in enumerate(streamed_features):
            feature.update(streamed_songs[i])

        return streamed_features

    @classmethod
    def _search_for_song(cls, song, artist, token):
        spotify = spotipy.Spotify(auth=token)
        results = spotify.search(q=f'{song} {artist}', type='track')
        first_result = results['tracks']['items'][0]
        return first_result['id']

    @classmethod
    def _get_song_info(cls, song_ids, token):
        spotify = spotipy.Spotify(auth=token)
        try:
            return spotify.audio_features(song_ids)
        except:
            return None

    @classmethod
    def _get_token(cls):
        return spotipy.util.prompt_for_user_token(
            username=SPOTIFY_USERNAME,
            scope=SPOTIFY_SCOPE,
            client_id = SPOTIFY_API_PUBLIC,
            client_secret = SPOTIFY_API_PRIVATE,
            redirect_uri = SPOTIFY_REDIRECT_URL
        )

class Fitbit():
    class SleepScoreReader(Reader):
        @classmethod
        def read_data(cls):
            with Path('data/fitbit/sleep-score/sleep_score.csv').open() as f:
                return [dict(x) for x in csv.DictReader(f)]

        @classmethod
        def get_data(cls):
            data = cls.read_data()
            return [SleepScore.from_dict(datum) for datum in data]

    class WeightReader(Reader):
        @classmethod
        def get_data(cls):
            data = cls.read_data('data/fitbit/user-site-export/weight*.json')
            return [
                Weight(extract_timestamp(datum['date'], datum['time']), datum['weight'])
                for datum in data
            ]

    class HeartRateReader(Reader):
        @classmethod
        def get_data(cls):
            data = cls.read_data('data/fitbit/user-site-export/heart_rate*.json')
            return [
                HeartRateReading(
                    extract_timestamp(*datum['dateTime'].split(' ')),
                    datum['value']['bpm']
                )
                for datum in data
            ]

if __name__ == '__main__':
    pprint(Fitbit.WeightReader.get_data()[:2])
    pprint(Fitbit.SleepScoreReader.get_data()[:2])
    pprint(SpotifyReader.get_data()[:2])
    print(Fitbit.HeartRateReader.get_data()[:2])
