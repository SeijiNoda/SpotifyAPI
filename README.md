# Spotify API Playlist Maker
> Script and Server made in Python that when working together generates a Spotify playlist with a mix of your most streamed tracks and most recently liked songs

### [The Server](./app.py)
This projecet interacts with the [Spotify API](https://developer.spotify.com/) with this web server. It hanldes all of the _OAuth_, login, and endpoints needed for the script to be able to create/update the playlist with all of it's tracks.<br>
It was built using [Flask](https://flask.palletsprojects.com/en/2.2.x/) for routing and the [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/#) library for easier access to the API.<br>
The <code>caller.py</code> script only calls the root route <code>localhost:[DOT_ENV_PORT]/</code>, witch then redirects itself to all other nescessary endpoints provided by the server. <br>
As the endpoints are locally ran on localhost, this server is independent on the script, but it would not be automated without it. However, if desired, the user could only run this file and make your own calls to this server, and the correct flow would still ve followed

### [The Script](./caller.py)
When running the .bat files, this is the second file to be opened. It starts after the server is set to run, and will make the calls for the creation of the playlist. After making the GET request to <code>localhost:[DOT_ENV_PORT]/</code>, it also tries to close the tab itself opened in the borwser.

## Built with
- [Python 3](https://www.python.org/) - as the general language used
  - [Flask](https://flask.palletsprojects.com/en/2.2.x/) - for the API access local server
  - [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/#) - for easier access and management to the Spotify Web API and _OAuth_
  - [python-dotenv](https://pypi.org/project/python-dotenv/) - for API keys and PORT management in development (this is replaceable if ran only locally)
- [Spotify for Developers](https://developer.spotify.com/) - for their awesome Web API that allowed this project to happen