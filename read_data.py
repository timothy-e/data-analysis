import csv
import datetime
import json
import os
from pprint import pprint
import spotipy
from pathlib import Path

SPOTIFY_API_PUBLIC = os.environ.get('SPOTIFY_API_PUBLIC')
SPOTIFY_API_PRIVATE = os.environ.get('SPOTIFY_API_PRIVATE')
SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USERNAME')
SPOTIFY_REDIRECT_URL = os.environ.get('SPOTIFY_REDIRECT_URL')
SPOTIFY_SCOPE = 'user-read-recently-played'

def read_spotify_data():
    def open_file(path):
        with path.open() as f:
            return json.load(f)

    files = Path('data/spotify').glob('StreamingHistory*.json')
    return [
        song
        for file in files
        for song in open_file(file)
    ]

def search_for_song(song, artist, token):
    spotify = spotipy.Spotify(auth=token)
    results = spotify.search(q=f'{song} {artist}', type='track')
    first_result = results['tracks']['items'][0]
    return first_result['id']


def get_song_info(song_ids, token):
    spotify = spotipy.Spotify(auth=token)
    try:
        return spotify.audio_features(song_ids)
    except:
        return None

def get_token():
    return spotipy.util.prompt_for_user_token(
        username=SPOTIFY_USERNAME,
        scope=SPOTIFY_SCOPE,
        client_id = SPOTIFY_API_PUBLIC,
        client_secret = SPOTIFY_API_PRIVATE,
        redirect_uri = SPOTIFY_REDIRECT_URL
    )

def get_songs():
    token = get_token()

    streamed_songs = read_spotify_data()
    streamed_ids = [
        search_for_song(song['trackName'], song['artistName'], token)
        for song in streamed_songs
    ]
    streamed_features = [
        info
        for i in range(0, len(streamed_ids), 50)
        for info in get_song_info(streamed_ids[i:i+50], token)
    ]

    for i, feature in enumerate(streamed_features):
        feature.update(streamed_songs[i])

    return streamed_features

def read_sleep_scores():
    def rename_timestamp(datum):
        datum['datetime'] = datum['timestamp']
        datum['timestamp'] = datetime.datetime.strptime(
            datum['timestamp'],
            "%Y-%m-%dT%H:%M:%SZ"
        ).timestamp()
        return datum

    file = Path('data/fitbit/sleep-score/sleep_score.csv')
    with file.open() as f:
        return [rename_timestamp(dict(x)) for x in csv.DictReader(f)]

def read_weight():
    def extract_timestamp(date, time):
        month, day, year = [int(d) for d in date.split("/")]
        h, m, s = [int(t) for t in time.split(":")]
        return datetime.datetime(2000 + year, month, day, h, m, s).timestamp()

    def open_weight_file(file):
        with file.open() as f:
            data = json.load(f)
            return [(extract_timestamp(datum['date'], datum['time']), datum['weight']) for datum in data]

    times = []
    weight = []
    files = sorted(Path('data/fitbit/user-site-export').glob('weight*.json'))
    return [
        datum
        for file in files
        for datum in open_weight_file(file)
    ]

if __name__ == '__main__':
    # pprint(read_weight())
    # pprint(read_sleep_scores())
    # pprint(get_songs())
    pass
