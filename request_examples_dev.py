from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from urllib.parse import urlencode
import webbrowser

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

auth_headers = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": "http://localhost:7777/callback",
    "scope": "user-library-read"
}

webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

def get_token():
    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists")
        return None

    return json_result[0]

def get_tracks(token, username):
    # url = f"https://api.spotify.com/v1/users/{username}/playlists"
    # url = "https://api.spotify.com/v1/playlists/4DO3Te0sTIZRfS9l8PGVuX/tracks"
    url = f"https://api.spotify.com/v1/me"
    headers = { "Authorization": f"Bearer {token}" }

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

token = get_token()
# result = search_for_artist(token, "Beatles")
result = get_tracks(token, input("Username: "))
print(result["items"][1]["name"])