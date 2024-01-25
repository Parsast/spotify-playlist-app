import json
with open("saved_tracks.json", 'r') as f:
        tracks = json.load(f)
print(len(tracks["items"]))