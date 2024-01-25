import json
import requests
import logging
import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import argparse
import time
import random

class cluster_kmeans():
    def __init__(self,json_file, client_id, client_secret,
                access_token, token_expiry_time):
        self.json_file = json_file
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry_time = token_expiry_time

    def request_spotify_access_token(self):
        
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

    def kmeans(self,k, n):
        with open(self.json_file, "r") as f:
            data = json.load(f)

        track_features = []
        track_names = []
        features_keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']

        for track in data:
            feature = []
            for key in features_keys:
                feature.append(track["audio_features"][key])
            track_features.append(feature)
            track_names.append(track["track"]["name"])

        X = np.array(track_features)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=k, random_state=0)
        clusters = kmeans.fit_predict(X_scaled)
        clusters = clusters.tolist()
        clusters_dic = {}
        for i in range(len(clusters)):
            if clusters[i] in clusters_dic.keys():
                clusters_dic[clusters[i]] += [i]
            else:
                clusters_dic[clusters[i]] = [i]
        chosen_cluster = random.randint(0, k-1)
        chosen = random.choices(clusters_dic[chosen_cluster], k=n)
        artists = []
        tracks = []
        for i,choice in enumerate(chosen):

            artists.append(data[choice]['track']['artists'][0]["id"])
            tracks.append(data[choice]['track']["id"])

        return (artists, tracks)

    def get_recommended_tracks(self,seed_artists, seed_tracks, limit=5,
                                target_acousticness=None,
                                target_danceability=None,
                                target_energy=None,
                                target_liveness=None,
                                target_loudness=None,
                                target_speechiness=None,
                                target_tempo=None,
                                target_valence=None):
        
        seed_artists = ",".join(seed_artists)
        seed_tracks = ",".join(seed_tracks)
        
        params = {
            # "seed_genres":"pop",
            'limit': limit,
            'seed_artists': seed_artists,
            'seed_tracks': seed_tracks,
            'target_acousticness': target_acousticness,
            'target_danceability': target_danceability,
            'target_energy': target_energy,
            'target_liveness': target_liveness,
            'target_loudness': target_loudness,
            'target_speechiness': target_speechiness,
            'target_tempo': target_tempo,
            'target_valence': target_valence
        }

        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}

        url = 'https://api.spotify.com/v1/recommendations'
        self.request_spotify_access_token()
        headers = {'Authorization': f'Bearer {self.access_token}'}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
        return []

# test = cluster_kmeans("saved_tracks.json",
#                      os.getenv('SPOTIFY_CLIENT_ID'),
#                      os.getenv('SPOTIFY_CLIENT_SECRET'),None, 3600)

# artists, tracks = test.kmeans(k =5, n = 1)
# # print(artists)
# # print(tracks)
# tracks = test.get_recommended_tracks(seed_artists = artists, seed_tracks = tracks)
# # print (artists)
# print (tracks)