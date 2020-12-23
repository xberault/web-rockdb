import click
from .app import app, db
import yaml
from .models import Artist, Album, Genre, Classification

@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    ''' Creates the tables and populates them with data. '''
    # creation de toutes les tables
    db.create_all()
    albums = yaml.load(open (filename))

    #creation des auteurs
    artists = {}
    for al in albums:
        ar = al["by"]
        if ar not in artists:
            o = Artist(name = ar)
            db.session.add(o)
            artists[ar] = o
    db.session.commit()

    #creation des genres
    genres = {}
    for al in albums:
        for g in al["genre"]:
            g = g.lower()
            if g not in genres:
                o = Genre(name = g)
                db.session.add(o)
                genres[g] = o
    db.session.commit()

    #creation des livres
    for al in albums:
        ar = artists[al["by"]]
        o = Album(
            title = al["title"],
            release = al["releaseYear"],
            img = al["img"],
            artist_id = ar.id
        )
        db.session.add(o)
    db.session.commit()

    #creation des classifications (relation entre livres et genres)
    for al in albums:
        al_id = Album.query.filter_by(title=al["title"]).first().id
        for g in al["genre"]:
            g = g.lower()
            g_id = Genre.query.filter_by(name=g).first().id
            o = Classification(album_id = al_id, genre_id = g_id)
            db.session.add(o)
    db.session.commit()

@app.cli.command()
def syncdb():
    ''' Creates all missing tables '''
    db.create_all()
