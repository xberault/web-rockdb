import click
from .app import app, db
import yaml
from .models import Artist, Album, Genre, Classification, User


@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    ''' Creates the tables and populates them with data. '''
    # creation de toutes les tables
    db.create_all()
    albums = yaml.safe_load(open(filename))

    # creation des artistes
    artists = {}
    for al in albums:
        ar = al["by"]
        if ar not in artists:
            o = Artist(name=ar)
            db.session.add(o)
            artists[ar] = o
        # p = al["parent"]
        # if p not in artists:
        #     o = Artist(name=p)
        #     db.session.add(o)
        #     artists[ar] = o
    db.session.commit()

    # creation des genres
    genres = {}
    for al in albums:
        for g in al["genre"]:
            g = g.lower()
            if g not in genres:
                o = Genre(name=g)
                db.session.add(o)
                genres[g] = o
    db.session.commit()

    # creation des livres
    for al in albums:
        ar = artists[al["by"]]
        # p = artists[al["parent"]]
        o = Album(
            title=al["title"],
            release=al["releaseYear"],
            img=al["img"],
            artist_id=ar.id,
            # parent_id=p.id
            parent=al["parent"]
        )
        db.session.add(o)
    db.session.commit()

    # creation des classifications (relation entre livres et genres)
    for al in albums:
        al_id = Album.query.filter_by(title=al["title"]).first().id
        for g in al["genre"]:
            g = g.lower()
            g_id = Genre.query.filter_by(name=g).first().id
            o = Classification(album_id=al_id, genre_id=g_id)
            db.session.add(o)
    db.session.commit()


@app.cli.command()
def syncdb():
    ''' Creates all missing tables '''
    db.create_all()


@app.cli.command()
@click.argument('username')
@click.argument('password')
def newuser(username, password):
    ''' Creates a new user '''
    return User.register(username, password)


@app.cli.command()
@click.argument('username')
@click.argument('password')
def passwd(username, password):
    ''' Changes password of an existing user '''
    u = User.query.get(username)
    if u:
        u.set_password(password)
    else:
        print("*" * 50)
        print("Il n'y a pas de compte associé au pseudo " + username)
        print("*" * 50)
