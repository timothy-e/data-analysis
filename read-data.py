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

def read_data():
    def open_file(path):
        with path.open() as f:
            return json.load(f)

    files = Path('data/spotify/').glob('StreamingHistory*.json')
    return [song for file in files for song in open_file(file)]

def search_for_song(song, artist, token):
    spotify = spotipy.Spotify(auth=token)
    song = spotify.search(q=f'{song} {artist}', type='track')['tracks']['items'][0]
    return song['id']


def get_song_info(song_ids, token):
    print(f"song tokens: {song_ids}")
    spotify = spotipy.Spotify(auth=token)
    try:
        features = spotify.audio_features(song_ids)
        return features[0]
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

if __name__ == '__main__':
    token = get_token()
    streamed_songs = read_data()
    pprint(streamed_songs)
    streamed_ids = [search_for_song(song['trackName'], song['artistName'], token) for song in streamed_songs]
    pprint(streamed_ids)
    streamed_features = [get_song_info(streamed_ids[i:i+50], token) for i in range(0, len(streamed_ids), 50)]
    pprint(streamed_features)
