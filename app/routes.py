from flask import render_template, redirect, request, session,url_for
from .add_features import add_feature
import json
import requests
import os
from app import app
from recommend.cluster import cluster_kmeans

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
SCOPE = 'user-library-read'
app.secret_key = 'STUInbjbjbnwert34'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    auth_url = 'https://accounts.spotify.com/authorize'
    params = {
        'response_type':'code',
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri':REDIRECT_URI
    }
    url = requests.Request('GET', auth_url,params = params).prepare().url
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url, data=token_data)
    response_data = response.json()
    access_token = response_data.get('access_token')

    # TODO: Store the token in the session (or a more secure place)
    session['access_token'] = access_token

    return redirect(url_for('get_saved_tracks'))

@app.route('/get-saved-tracks')
def get_saved_tracks():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/start')  # Redirect to start if no token

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    all_tracks = []
    saved_tracks_url = 'https://api.spotify.com/v1/me/tracks'
    # while saved_tracks_url:
    #     response = requests.get(saved_tracks_url, headers=headers)
    #     if response:
    #         response = response.json()
    #         all_tracks.extend(response.get("items",[]))
    #         saved_tracks_url = response.get("next")
    #   # Redirect back to the index page
    #     else:
    #         break

    # with open('saved_tracks.json', 'w') as file:
    #     json.dump(all_tracks, file, indent=4)
    
    # add_features_instance  = add_feature("saved_tracks.json",
    #                 os.getenv('SPOTIFY_CLIENT_ID'),
    #                  os.getenv('SPOTIFY_CLIENT_SECRET'),
    #                  None,
    #                  3600)
    # m = add_features_instance.get_audio_features_track()
    # with open("features.json", "w") as f:
    #     json.dump(m,f, indent = 4)

    return redirect(url_for('preferences'))

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    size = None
    danceability = None
    acousticness = None
    energy = None
    liveness = None
    loudness = None
    speechiness = None
    tempo = None
    valence = None
    if request.method == 'POST':
        size = request.form.get("size")
        danceability = request.form.get('danceability')
        acousticness = request.form.get('acousticness')
        energy = request.form.get("energy")
        liveness = request.form.get("liveness")
        loudness = request.form.get("loudness")
        speechiness = request.form.get("speechiness")
        tempo = request.form.get("tempo")
        valence = request.form.get("valence")
        try:
            danceability = float(danceability)
            acousticness = float(acousticness)
            size = int(size)
            target_energy = float(energy)
            liveness = float(liveness)
            loudness = float(loudness)
            speechiness = float(speechiness)
            tempo = float(tempo)
            valence =  float(valence)
            if not (1<= size <=20):
                raise ValueError("The parameter size must be a integer between 1 to 20")
            if not (0 <=danceability <=1):
                raise ValueError("must be between 0 and 1")
            if not (0 <=acousticness <=1):
                raise ValueError("must be between 0 and 1")
            if not (0 <= target_energy <=1):
                raise ValueError("energy value must be between 0 to 1")
            if not (0 <= liveness <= 1):
                raise ValueError("liveness value must be between 0 to 1")
            if not (0 <=speechiness <= 1):
                raise ValueError("speechiness value must be between 0 to 1")
            if not (tempo >= 0):
                raise ValueError("Tempo value must be bigger than 0")
            if not (valence >= 0):
                raise ValueError("Valence value must be between 0 and 1")
            

            return redirect(url_for('index'))  
        except ValueError as e:
            return render_template('preferences.html', error = str(e))
        clusters = cluster_kmeans("saved_tracks.json",
                                        os.getenv('SPOTIFY_CLIENT_ID'),
                                        os.getenv('SPOTIFY_CLIENT_SECRET'),None, 3600)
        artists, tracks = clusters.kmeans(k =5, n = 1)
        recommended_tracks = clusters.get_recommended_tracks(seed_artists = artists,
                                                        seed_tracks = tracks, 
                                                        target_energy= target_energy)
        with open("recommendations.json", "w")as f:
            json.dump(recommended_tracks, f, indent = 4)
    return render_template('preferences.html')