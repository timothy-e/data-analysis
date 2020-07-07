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

def get_songs(token):
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

if __name__ == '__main__':
    token = get_token()
    pprint(get_songs(token))
