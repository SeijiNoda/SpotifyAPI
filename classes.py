class Track:
    def __init__(self, track_name, track_id, artist_name):
        self.track_name = track_name
        self.track_id = track_id
        self.artist_name = artist_name

    def to_string(self):
        return self.track_name + ' by ' + self.artist_name
