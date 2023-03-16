class Track:
    def __init__(self, track_name, track_uri, artist_name):
        self.track_name = track_name
        self.track_uri = track_uri
        self.artist_name = artist_name

    def to_string(self):
        return self.track_name + ' by ' + self.artist_name
