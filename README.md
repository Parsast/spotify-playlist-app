# Spotify Playlist App

## Introduction
Spotify Playlist App is a Flask web application that allows users to generate personalized Spotify playlists based on their music preferences. This project aims to provide music lovers with a unique way to discover and enjoy new music tailored to their tastes.

## Features
- **Spotify Authentication**: Securely authenticate with Spotify using OAuth to access your music library.
- **Music Library Analysis**: Retrieve your saved tracks from Spotify to understand your music preferences.
- **Personalized Playlist Generation**: Utilize K-Means clustering to create playlists based on the acoustic features of tracks.
- **Custom Recommendations**: Get music recommendations based on your specific preferences.

## Requirements
- Python 3.6+
- Flask, requests, numpy, pandas, scikit-learn


## Installation
1. Clone this repository to your local machine.
2. Install required Python libraries.

## Getting Started
1. Set your Flask application environment variable:

   export FLASK_APP=spotify.py
2. Start the Flask server:

   flask run

3. Open your browser and navigate to `http://127.0.0.1:5000/index`.


## License
This project is licensed under the MIT License - see the LICENSE file for details.
