from .app import db, login_manager
from flask_login import UserMixin

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f"<Artiste ({self.id}) {self.name}>"

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
        backref = db.backref("albums", lazy="dynamic"))

    def __repr__(self):
        return f"<Album ({self.id}) {self.title}>"

class Classification(db.Model):
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), primary_key=True)

    album = db.relationship(
        "Album",
        backref = db.backref("classifications", lazy="dynamic"))

    genre = db.relationship(
        "Genre",
        backref = db.backref("classifications", lazy="dynamic"))

def get_sample():
    return Album.query.limit(10).all()

def get_artist(id):
    return Artist.query.get(id)

def get_genre(id):
    return Genre.query.get(id)

def get_album(id):
    return Album.query.get(id)

class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)
