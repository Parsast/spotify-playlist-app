import json
import requests
import time
import logging
import os
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class add_feature():
    def __init__(self, json_file,client_id,client_secret, access_token, token_expiry_time):
        self.json_file = json_file
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry_time = token_expiry_time

    def request_spotify_access_token(self):
        # global access_token, token_expiry_time
        url = 'https://accounts.spotify.com/api/token'
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        self.access_token = data['access_token']
        # Refresh token every 50 minutes (3000 seconds)
        self.token_expiry_time = time.time() + 3000

    def check_token_refresh(self):
        # global access_token, token_expiry_time
        if not self.access_token or time.time() > self.token_expiry_time:
            logging.info("Refreshing Spotify access token...")
            self.request_spotify_access_token()
    def get_audio_features_track(self):
        features = []
        with open(self.json_file, 'r') as f:
            tracks = json.load(f)
        for track in tracks:
            track_id = track["track"]["id"]
            self.check_token_refresh()
            url = f'https://api.spotify.com/v1/audio-features/{track_id}'
            headers = {'Authorization': f'Bearer {self.access_token}'}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                response = response.json()
                track["audio_features"] = response
                features.append(response)

            except requests.RequestException as e:
                logging.error(f"Error retrieving audio features for track {track_id}: {e}")
        with open(self.json_file, 'w') as f:
            json.dump(tracks,f, indent = 4)
        if features != []:
            return features
        else: return None

test  = add_feature("saved_tracks.json",
                    os.getenv('SPOTIFY_CLIENT_ID'),
                     os.getenv('SPOTIFY_CLIENT_SECRET'),
                     None,
                     3600)

# m = test.get_audio_features_track()
# with open("f.json", 'w') as file:
#     json.dump(m, file, indent=4)
