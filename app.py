from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
from dotenv import load_dotenv

import time

import secrets
import string

from classes import *

app = Flask(__name__)

random_str = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
app.secret_key = random_str
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

@app.route('/deredirect')
def deredirect():
    # been having infinte-loop problems sometimes when authenticating, and according to https://stackoverflow.com/questions/61198574/spotify-api-authorization-redirects-too-many-times,
    # the solution is to simply re-redirect (or deredirect) the call to another module, hence this route

    return redirect(url_for('create_playlist', _external=True))

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
    return redirect(url_for('deredirect', _external=True))

@app.route('/createPlaylist')
def create_playlist():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    #
    # get current user's profile (need user ID for creating playlist and display name) (*)
    # get current user's playlists 
    # check if current user has a playlist called "[user's display name from (*)]'s AutoPlaylist"
    #   if he doesn't have, create a new playlist [POST] (using user's ID from (*)) and get it's ID from the response from the POST request
    #
    #   if he has, get it's ID from the response in ['items'][i]['id']
    #       remove all songs [DELETE] from the previous playlist
    #
    # get tracks to be added to the new playlist
    # create a string concatenating all songs from the seleceted tracks by their URI's and separeted by a comma ','
    # with the playlist's ID and the URI's string, add all the songs to the playlist [POST]
    #
    user = get_current_user()
    playlist_name = f'{user.display_name}\'s AutoPlaylist'
    playlist_dscrptn = f'This playlist was procedurally genereated at {str(time.asctime())}'
    playlists = get_current_user_playlists()
    
    #
    # verify if "[current user's name]'s AutoPlaylist already exists or not, and if it does, get it's ID code" 
    #
    playlist_exists = False
    playlist_id = -1
    end = False
    while True:
        for index, playlist in enumerate(playlists):
            if playlist.name == playlist_name:
                playlist_exists = True
                playlist_id = playlist.id
                break
        
        if playlist_exists or end:
            break
        
        playlists = get_current_user_playlists(offset=(index+1)*20)
        
        if len(playlists) < 20:
            end = True   
    
    # 
    # query string for n tracks should follow this format: '[track_one_uri],[track_two_uri],...,[track_n_uri]'
    #
    tracks = get_tracks()
    tracks_uri_str = ''
    for index, track in enumerate(tracks):
        tracks_uri_str += track.uri
        if index < len(tracks) - 1:
            tracks_uri_str += ','
    
    #
    # using playlist_exists, creates/updates the playlist with the new songs
    #
    if playlist_exists:
        # delete songs from playlist
        # insert new songs
        sp.playlist_replace_items(playlist_id=playlist_id, items=(track.uri for track in tracks))
        sp.playlist_change_details(playlist_id=playlist_id, description=playlist_dscrptn)
        return f'playlist already exists!'
    else:
        playlist_id = create_new_playlist(name=playlist_name, user=user.uid, description=playlist_dscrptn, public=True)
        add_tracks_to_playlist(playlist_id=playlist_id, tracks=(track.uri for track in tracks))
        return f'playlist created at https://open.spotify.com/playlist/{str(playlist_id)}' 
    

    return f'creating your playlist...<br><br>{tracks_uri_str}'

def get_tracks():
    top_tracks = get_top_tracks(limit = 20)
    saved_tracks = get_saved_tracks()

    #
    # get most recent tracks
    # get top tracks
    # 
    # afterwards, verify if there is any repeated song from the recent tracks amongst the top tracks (*)
    #   if there is, remove such song from the top tracks list
    # 
    # afterwards, verify if the list of top track is still larger than 15
    #   if it is not, request for more top tracks with ofset equal to 15 and repeat step (*)
    #
    # create playlist with the given lists
    #

    correct_size = False
    while not correct_size:
        for saved_track in saved_tracks:
            for index, top_track in enumerate(top_tracks):
                if saved_track.name == top_track.name:
                    top_tracks.pop(index)
                    
                    # Here we break since we do not expect to have the same song twice in a list, however if that were to happen, we would need to alter this code to
                    # take that in consideration since the indexes would be wrong after the first .pop(index).
                    # To avoid possibly having an index out of range crash, this break will do (and it also makes the code slightly faster :D).
                    break
        
        correct_size = True
        len_top_tracks = len(top_tracks)
        if (len_top_tracks < 15):
            correct_size = False
            top_tracks += get_top_tracks(limit = 15 - len_top_tracks, offset = 15)
                

    print_tracks(top_tracks)
    print_tracks(saved_tracks)

    return top_tracks + saved_tracks
    #return sp.current_user_saved_tracks(limit=10)

def get_top_tracks(limit, offset=0):
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # get current user's top tracks
    results = sp.current_user_top_tracks(limit = limit, time_range='short_term', offset=offset)
    top_tracks = []
    for _, track in enumerate(results['items']):
        new_track = Track(track['name'], track['uri'], track['artists'][0]['name'])
        top_tracks.append(new_track)

    return top_tracks

def get_saved_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    results = sp.current_user_saved_tracks(limit=15)
    saved_tracks = []
    for _, item in enumerate(results['items']):
        track = item['track']
        new_track = Track(track['name'], track['uri'], track['artists'][0]['name'])
        saved_tracks.append(new_track)

    return saved_tracks

def get_current_user():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    results = sp.current_user()
    user = User(results['id'], results['display_name'])

    return user
 
def get_current_user_playlists(limit=20, offset=0):
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    results = sp.current_user_playlists(limit=limit, offset=offset)
    playlists = []
    for item in results['items']:
        new_playlist = Playlist(item['id'], item['name'], item['owner']['id'], item['owner']['display_name'])
        playlists.append(new_playlist)

    return playlists

def create_new_playlist(name, user, description, public=True, collab=False):
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # creates a new playlist given the user's ID, name, if he wants that playlist ot public, and it's description
    results = sp.user_playlist_create(user=user, name=name, public=public, collaborative=collab, description=description)
    playlist_id = results['id']
    
    return playlist_id

def add_tracks_to_playlist(playlist_id, tracks, position=0):
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    # adds the tracks to the given playlist ID
    results = sp.playlist_add_items(playlist_id=playlist_id, items=tracks, position=position)
    snapshot_id = results['snapshot_id']
    return snapshot_id


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
        scope='user-library-read user-top-read playlist-modify-private playlist-modify-public'
    )

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.get('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
# aux funcs

def print_tracks(track_list):
    for i in range(len(track_list)):
        print(str(i) + '. ' + str(track_list[i].to_string()))

server_port = os.getenv('PORT')

if __name__ == '__main__':
    app.run(host='localhost', port=server_port, debug=False)
