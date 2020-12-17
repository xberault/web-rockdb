from .app import db

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f"<Artiste ({self.id}) {self.name}>"

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    release = db.Column(db.Integer)
    img = db.Column(db.String(100))

    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = db.relationship("Artist", backref = db.backref("albums", lazy="dynamic"))

    #genre
    #parent

    def __repr__(self):
        return f"<Album ({self.id}) {self.title}>"

def get_sample():
    return Album.query.limit(10).all()