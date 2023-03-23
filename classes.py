class Track:
    def __init__(self, name, uri, artist_name):
        self._name = name
        self._uri = uri
        self._artist_name = artist_name

    @property
    def name(self):
        return self._name

    @property
    def uri(self):
        return self._uri

    @property
    def artist_name(self):
        return self._artist_name

    def to_string(self):
        return self.name + ' by ' + self.artist_name


class User:
    def __init__(self, uid, display_name):
        self._uid = uid
        self._display_name = display_name
    
    @property
    def uid(self):
        return self._uid

    @property
    def display_name(self):
        return self._display_name

    def to_string(self):
        return self.display_name


class Playlist:
    def __init__(self, playlist_id, name, owner_uid, owner_display_name):
        self._id = playlist_id
        self._name = name
        self._owner = User(owner_uid, owner_display_name)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def owner(self):
        return self._owner

    def to_string(self):
        return self.name + ', playlist made by ' + self.owner.display_name