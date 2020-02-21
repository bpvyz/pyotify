from pyotify import Spotify
import json
import os

client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

sp = Spotify(client_id, client_secret)

print(json.dumps(response, indent=4, sort_keys=True))