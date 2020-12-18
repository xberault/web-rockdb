from .app import db

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f"<Artiste ({self.id}) {self.name}>"

# genres = db.Table("genres",
#     db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True),
#     db.Column("album_id", db.Integer, db.ForeignKey("album.id"), primary_key=True)
# )

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

    # genres = db.relationship(
    #     "Genre",
    #     secondary = genres,
    #     lazy = "subquery",
    #     backref = db.backref("albums", lazy="dynamic"))
    #parent

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
