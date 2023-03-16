from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
from dotenv import load_dotenv

import time

import secrets
import string

from classes import Track

app = Flask(__name__)

random_str = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
app.secret_key = random_str
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('create_playlist', _external=True))

@app.route('/createPlaylist')
def create_playlist():
    tracks = get_tracks()

    return 'creating your playlist...<br><br>' + tracks[0].track_name

def get_tracks():
    top_tracks = get_top_tracks()
    saved_tracks = get_saved_tracks()

    return top_tracks + saved_tracks
    #return sp.current_user_saved_tracks(limit=10)

def get_top_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # get current user's top tracks
    results = sp.current_user_top_tracks(limit = 20, time_range='short_term')
    top_tracks = []
    for _, track in enumerate(results['items']):
        new_track = Track(track['name'], track['id'], track['artists'][0]['name'])
        top_tracks.append(new_track)

    return top_tracks

def get_saved_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    results = sp.current_user_saved_tracks(limit=20)
    saved_tracks = []
    for _, item in enumerate(results['items']):
        track = item['track']
        new_track = Track(track['name'], track['id'], track['artists'][0]['name'])
        saved_tracks.append(new_track)

    return saved_tracks


def get_token():
    token_valid = False
    token_info = session.get('token_info', {})
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))
    
    token_valid = True
    return token_info, token_valid

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-library-read user-top-read'
    )