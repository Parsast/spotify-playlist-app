import json
import requests
import logging
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import argparse
import time
import random

access_token = None
token_expiry_time = None

def request_spotify_access_token(client_id,client_secret):
    global access_token, token_expiry_time
    url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    data = response.json()
    access_token = data['access_token']
    # Refresh token every 50 minutes (3000 seconds)
    token_expiry_time = time.time() + 3000




def get_recommended_tracks(seed_artists, seed_tracks, access_token, limit=5,
                           min_acousticness=None, max_acousticness=None, target_acousticness=None,
                           min_danceability=None, max_danceability=None, target_danceability=None,
                           min_duration_ms=None, max_duration_ms=None, target_duration_ms=None,
                           min_energy=None, max_energy=None, target_energy=None,
                           min_instrumentalness=None, max_instrumentalness=None, target_instrumentalness=None,
                           min_key=None, max_key=None, target_key=None,
                           min_liveness=None, max_liveness=None, target_liveness=None,
                           min_loudness=None, max_loudness=None, target_loudness=None,
                           min_mode=None, max_mode=None, target_mode=None,
                           min_popularity=None, max_popularity=None, target_popularity=None,
                           min_speechiness=None, max_speechiness=None, target_speechiness=None,
                           min_tempo=None, max_tempo=None, target_tempo=None,
                           min_time_signature=None, max_time_signature=None, target_time_signature=None,
                           min_valence=None, max_valence=None, target_valence=None):
    
    seed_artists = ",".join(seed_artists)
    seed_tracks = ",".join(seed_tracks)
    
    params = {
        'limit': limit,
        'seed_artists': seed_artists,
        'seed_tracks': seed_tracks,
        'min_acousticness': min_acousticness,
        'max_acousticness': max_acousticness,
        'target_acousticness': target_acousticness,
        'min_danceability': min_danceability,
        'max_danceability': max_danceability,
        'target_danceability': target_danceability,
        'min_duration_ms': min_duration_ms,
        'max_duration_ms': max_duration_ms,
        'target_duration_ms': target_duration_ms,
        'min_energy': min_energy,
        'max_energy': max_energy,
        'target_energy': target_energy,
        'min_instrumentalness': min_instrumentalness,
        'max_instrumentalness': max_instrumentalness,
        'target_instrumentalness': target_instrumentalness,
        'min_key': min_key,
        'max_key': max_key,
        'target_key': target_key,
        'min_liveness': min_liveness,
        'max_liveness': max_liveness,
        'target_liveness': target_liveness,
        'min_loudness': min_loudness,
        'max_loudness': max_loudness,
        'target_loudness': target_loudness,
        'min_mode': min_mode,
        'max_mode': max_mode,
        'target_mode': target_mode,
        'min_popularity': min_popularity,
        'max_popularity': max_popularity,
        'target_popularity': target_popularity,
        'min_speechiness': min_speechiness,
        'max_speechiness': max_speechiness,
        'target_speechiness': target_speechiness,
        'min_tempo': min_tempo,
        'max_tempo': max_tempo,
        'target_tempo': target_tempo,
        'min_time_signature': min_time_signature,
        'max_time_signature': max_time_signature,
        'target_time_signature': target_time_signature,
        'min_valence': min_valence,
        'max_valence': max_valence,
        'target_valence': target_valence
    }

    # Filter out None values
    params = {k: v for k, v in params.items() if v is not None}

    url = 'https://api.spotify.com/v1/recommendations'
    
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            # Handle rate limit exceeded
            retry_after = int(response.headers.get("Retry-After", 60))
            logging.info(f"Rate limit reached. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return get_recommended_tracks(seed_artists, seed_tracks, access_token, limit,
                                          min_acousticness, max_acousticness, target_acousticness,
                                          min_danceability, max_danceability, target_danceability,
                                          min_duration_ms, max_duration_ms, target_duration_ms,
                                          min_energy, max_energy, target_energy,
                                          min_instrumentalness, max_instrumentalness, target_instrumentalness,
                                                      min_instrumentalness, max_instrumentalness, target_instrumentalness,
                                          min_key, max_key, target_key,
                                          min_liveness, max_liveness, target_liveness,
                                          min_loudness, max_loudness, target_loudness,
                                          min_mode, max_mode, target_mode,
                                          min_popularity, max_popularity, target_popularity,
                                          min_speechiness, max_speechiness, target_speechiness,
                                          min_tempo, max_tempo, target_tempo,
                                          min_time_signature, max_time_signature, target_time_signature,
                                          min_valence, max_valence, target_valence)
        else:
            logging.error(f"Error fetching recommended tracks: {e}")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
    return []

def kmeans(k, n):
    with open("../saved_tracks.json", "r") as f:
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
    chosen = random.choice(clusters_dic[chosen_cluster], k = n)
    artists = []
    tracks = []
    for i,choice in enumerate(chosen):

        artists.append(data[choice]['track']['artists'][0]["id"])
        tracks.append(data[choice]['track']["id"])

    return (artists, tracks)


    # clustered_tracks = pd.DataFrame({'Song Name': track_names, 'Cluster': clusters})


def main():
    request_spotify_access_token(os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET'))
    parser = argparse.ArgumentParser(description='Get Spotify track recommendations.')

    # Define arguments
    parser.add_argument('k', type=int , help='Number of clusters', default=5)
    parser.add_argument('n', type=int, help='Number of seed songs between 1 to 5', default=3)
    seed_artists, seed_tracks = kmeans(k,n)

    parser.add_argument('--limit', type=int, help='Number of tracks to return', default=5)

    # Add arguments for all the tunable track attributes
    parser.add_argument('--min_acousticness', type=float, help='Minimum acousticness')
    parser.add_argument('--max_acousticness', type=float, help='Maximum acousticness')
    parser.add_argument('--target_acousticness', type=float, help='Target acousticness')
    parser.add_argument('--min_danceability', type=float, help='Minimum danceability')
    parser.add_argument('--max_danceability', type=float, help='Maximum danceability')
    parser.add_argument('--target_danceability', type=float, help='Target danceability')
    parser.add_argument('--min_duration_ms', type=int, help='Minimum duration in milliseconds')
    parser.add_argument('--max_duration_ms', type=int, help='Maximum duration in milliseconds')
    parser.add_argument('--target_duration_ms', type=int, help='Target duration in milliseconds')
    parser.add_argument('--min_energy', type=float, help='Minimum energy')
    parser.add_argument('--max_energy', type=float, help='Maximum energy')
    parser.add_argument('--target_energy', type=float, help='Target energy')
    parser.add_argument('--min_instrumentalness', type=float, help='Minimum instrumentalness')
    parser.add_argument('--max_instrumentalness', type=float, help='Maximum instrumentalness')
    parser.add_argument('--target_instrumentalness', type=float, help='Target instrumentalness')
    parser.add_argument('--min_key', type=int, help='Minimum key')
    parser.add_argument('--max_key', type=int, help='Maximum key')
    parser.add_argument('--target_key', type=int, help='Target key')
    parser.add_argument('--min_liveness', type=float, help='Minimum liveness')
    parser.add_argument('--max_liveness', type=float, help='Maximum liveness')
    parser.add_argument('--target_liveness', type=float, help='Target liveness')
    parser.add_argument('--min_loudness', type=float, help='Minimum loudness')
    parser.add_argument('--max_loudness', type=float, help='Maximum loudness')
    parser.add_argument('--target_loudness', type=float, help='Target loudness')
    parser.add_argument('--min_mode', type=int, help='Minimum mode')
    parser.add_argument('--max_mode', type=int, help='Maximum mode')
    parser.add_argument('--target_mode', type=int, help='Target mode')
    parser.add_argument('--min_popularity', type=int, help='Minimum popularity')
    parser.add_argument('--max_popularity', type=int, help='Maximum popularity')
    parser.add_argument('--target_popularity', type=int, help='Target popularity')
    parser.add_argument('--min_speechiness', type=float, help='Minimum speechiness')
    parser.add_argument('--max_speechiness', type=float, help='Maximum speechiness')
    parser.add_argument('--target_speechiness', type=float, help='Target speechiness')
    parser.add_argument('--min_tempo', type=float, help='Minimum tempo in BPM')
    parser.add_argument('--max_tempo', type=float, help='Maximum tempo in BPM')
    parser.add_argument('--target_tempo', type=float, help='Target tempo in BPM')
    parser.add_argument('--min_time_signature', type=int, help='Minimum time signature')
    parser.add_argument('--max_time_signature', type=int, help='Maximum time signature')
    parser.add_argument('--target_time_signature', type=int, help='Target time signature')
    parser.add_argument('--min_valence', type=float, help='Minimum valence')
    parser.add_argument('--max_valence', type=float, help='Maximum valence')
    parser.add_argument('--target_valence', type=float, help='Target valence')

    args = parser.parse_args()

    # Call the get_recommended_tracks function with the parsed arguments
    recommendations = get_recommended_tracks(
        seed_artists=seed_artists,
        seed_tracks=seed_tracks,
        access_token=args.access_token,
        limit=args.limit,
        min_acousticness=args.min_acousticness,
        max_acousticness=args.max_acousticness,
        target_acousticness=args.target_acousticness,
        min_danceability=args.min_danceability,
        max_danceability=args.max_danceability,
        target_danceability=args.target_danceability,
        min_duration_ms=args.min_duration_ms,
        max_duration_ms=args.max_duration_ms,
        target_duration_ms=args.target_duration_ms,
        min_energy=args.min_energy,
        max_energy=args.max_energy,
        target_energy=args.target_energy,
        min_instrumentalness=args.min_instrumentalness,
        max_instrumentalness=args.max_instrumentalness,
        target_instrumentalness=args.target_instrumentalness,
        min_key=args.min_key,
        max_key=args.max_key,
        target_key=args.target_key,
        min_liveness=args.min_liveness,
        max_liveness=args.max_liveness,
        target_liveness=args.target_liveness,
        min_loudness=args.min_loudness,
        max_loudness=args.max_loudness,
        target_loudness=args.target_loudness,
        min_mode=args.min_mode,
        max_mode=args.max_mode,
        target_mode=args.target_mode,
        min_popularity=args.min_popularity,
        max_popularity=args.max_popularity,
        target_popularity=args.target_popularity,
        min_speechiness=args.min_speechiness,
        max_speechiness=args.max_speechiness,
        target_speechiness=args.target_speechiness,
        min_tempo=args.min_tempo,
        max_tempo=args.max_tempo,
        target_tempo=args.target_tempo,
        min_time_signature=args.min_time_signature,
        max_time_signature=args.max_time_signature,
        target_time_signature=args.target_time_signature,
        min_valence=args.min_valence,
        max_valence=args.max_valence,
        target_valence=args.target_valence
    )

    print(recommendations)

if __name__ == "__main__":
    main()

# # Print songs in each cluster
# for i in range(k):
#     print(f"Songs in Cluster {i}:")
#     print(clustered_tracks[clustered_tracks['Cluster'] == i]['Song Name'].values)
#     print()