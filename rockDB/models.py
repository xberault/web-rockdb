from .app import db, login_manager
from flask_login import UserMixin
from hashlib import sha256


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f"<Artiste ({self.id}) {self.name}>"

    @classmethod
    def from_id(cls, id):
        return Artist.query.get(id)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f"<Genre ({self.id}) {self.name}>"


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    release = db.Column(db.Integer)
    img = db.Column(db.String(100))

    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = db.relationship(
        "Artist",
        backref=db.backref("artist", lazy="dynamic"))

    def __repr__(self):
        return f"<Album ({self.id}) {self.title}>"


class Classification(db.Model):
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), primary_key=True)

    album = db.relationship(
        "Album",
        backref=db.backref("classifications", lazy="dynamic"))

    genre = db.relationship(
        "Genre",
        backref=db.backref("classifications", lazy="dynamic"))


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.username"))

    user = db.relationship(
        "User",
        backref=db.backref("playlists", lazy="dynamic"))


class Indexation(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"), primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), primary_key=True)

    playlist = db.relationship(
        "Playlist",
        backref=db.backref("indexations", lazy="dynamic"))

    album = db.relationship(
        "Album",
        backref=db.backref("indexations", lazy="dynamic"))


def get_sample():
    return Album.query.limit(10).all()


def get_artist(id):
    return Artist.query.get(id)


def get_genre(id):
    return Genre.query.get(id)


def get_album(id):
    return Album.query.get(id)


def get_albums(id_playlist):
    pass
    # return Album.query.filter()


@login_manager.user_loader
def load_user(username):
    return User.user_from_username(username)


class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))

    def __init__(self, username, password):
        super()
        self.username = username
        self.password = password

    def get_id(self):
        return self.username

    def check_password(self, password):
        """Check hashed password."""
        m = sha256()
        m.update(password.encode())
        password = m.hexdigest()
        return password == self.password

    def set_password(self, password):
        """
        change le mot de passe d'un utilisateur
        :param password:
        :return:
        """
        m = sha256()
        m.update(password.encode())
        self.password = m.hexdigest()
        db.session.commit()

    def __repr__(self):
        return self.username

    @classmethod
    def register(cls, username, password):
        """
        ajoute un utilisateur à la bd
        :param username:
        :param password:
        :return: l'utilisateur nouvellement crée
        """
        m = sha256()
        m.update(password.encode())
        u = User(username, m.hexdigest())
        db.session.add(u)
        db.session.commit()
        return u

    @classmethod
    def user_from_username(cls, username):
        return User.query.get(username)
