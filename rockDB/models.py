from .app import db, login_manager
from flask_login import UserMixin
from hashlib import sha256


# **************************************************************************** #
# ************************* gestion des artistes ***************************** #
# **************************************************************************** #

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    # ********** cration et ajout d'un artist dans la bd ********** #
    @classmethod
    def create_and_add(cls, name):
        """
        ajoute un artiste à la bd
        :param name:
        :return: l'artiste nouvellement créé
        """
        a = Artist(name=name)
        db.session.add(a)
        db.session.commit()
        return a

    # ********** modifications des attributs d'un album ********** #

    def set_name(self, name):
        self.name = name
        db.session.commit()

    @classmethod
    def delete(cls, artist_id):

        # suppression des relasions pour les genres
        albums = set(Artist.query.get(artist_id).albums.all())
        parents = set(Artist.query.get(artist_id).rights.all())

        albums = albums|parents 

        for album in albums:
            Album.delete(album.id)
            db.session.commit()

        db.session.delete(Artist.from_id(artist_id))
        db.session.commit()
    

    # ********** recupperation des artists ********** #

    @classmethod
    def artist_from_name(cls, name):
        return Artist.query.filter(Artist.name.like(name)).all()

    @classmethod
    def from_id(cls, id):
        return Artist.query.get(id)
    
    def __repr__(self):
        return f"<Artiste ({self.id}) {self.name}>"

def get_all_artist():
    return Artist.query.order_by(Artist.name).all()

def get_sample_artist_without_genre(filter_type, filter_value):
    if filter_type == "name":
        return Artist.query.filter(Artist.name.like('%'+filter_value+'%')).order_by(Artist.name)
    return Artist.query.order_by(Artist.name).all()

# **************************************************************************** #
# ************************** gestion des genres ****************************** #
# **************************************************************************** #

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    # ********** cration et ajout d'un genre dans la bd ********** #
    @classmethod
    def create_and_add(cls, name):
        """
        ajoute un genre à la bd
        :param name:
        :return: le genre nouvellement créé
        """
        g = Genre(name=name)
        db.session.add(g)
        db.session.commit()
        return g

    # ********** modifications des attributs d'un genre ********** #

    def set_name(self, name):
        self.name = name
        db.session.commit()

    @classmethod
    def delete(cls, genre_id):

        # suppression des relasions pour les genres
        classifications = Genre.query.get(genre_id).classifications.all()
        for c in classifications:
            db.session.delete(c)
            db.session.commit()

        db.session.delete(Genre.from_id(genre_id))
        db.session.commit()

    # ********** recupperation des genres ********** #

    @classmethod
    def genre_from_name(cls, name):
        return Genre.query.filter(Genre.name.like(name)).all()
    
    @classmethod
    def from_id(cls, id):
        return Genre.query.get(id)

    @classmethod
    def delete_if_no_relation(cls, id):
        classifications = Genre.query.get(id).classifications.all()
        if len(classifications) == 0:
            db.session.delete(Genre.query.get(id))
            db.session.commit()
    
    def __repr__(self):
        return f"<Genre ({self.id}) {self.name}>"

def get_sample_genre():
    return Genre.query.distinct().order_by(Genre.name)

def get_genres_id():
    genres = Genre.query.distinct().order_by(Genre.name).all()
    res = []
    for genre in genres:
        res.append(genre.id)
    return res

# **************************************************************************** #
# ************************** gestion des albums ****************************** #
# **************************************************************************** #

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    release = db.Column(db.Integer)
    img = db.Column(db.String(100))
    # parent = db.Column(db.String(100))

    parent_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    parent = db.relationship(
        "Artist",
        backref=db.backref("rights", lazy="dynamic"),
        foreign_keys=[parent_id])

    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = db.relationship(
        "Artist",
        backref=db.backref("albums", lazy="dynamic"),
        foreign_keys=[artist_id])

    # ********** cration et ajout d'un album dans la bd ********** #
    @classmethod
    def create_and_add(cls, title, release, img, artist_id, parent_id):
        """
        ajoute un album à la bd
        :param title:
        :param release:
        :param img:
        :param artist_id:
        :param parent:
        :return: l'album nouvellement créé
        """
        a = Album(
            title=title,
            release=release,
            img=img,
            artist_id=artist_id,
            parent_id=parent_id
        )
        db.session.add(a)
        db.session.commit()
        return a

    # ********** modifications des attributs d'un album ********** #

    def set_title(self, title):
        self.title = title
        db.session.commit()
    
    def set_release(self, release):
        self.release = release
        db.session.commit()

    def set_img(self, img):
        self.img = img
        db.session.commit()

    def set_artist_id(self, artist_id):
        self.artist_id = artist_id
        db.session.commit()
    
    def set_parent_id(self, parent_id):
        self.release = parent_id
        db.session.commit()
    
    def set_genres(self, release):
        pass


    @classmethod
    def delete(cls, album_id):

        # suppression des relasions pour les genres
        classifications = Album.query.get(album_id).classifications.all()
        genres = set()
        for c in classifications:
            genre_id = c.genre_id
            genres.add(genre_id)
            db.session.delete(c)
            db.session.commit()
        
        # Sera décommenter quand on pourra ajouter un genre
        # for genre_id in genres:
        #     Genre.delete_if_no_relation(genre_id)

        db.session.delete(Album.from_id(album_id))
        db.session.commit()
    
    # ********** recupperation des albums ********** #
    
    @classmethod
    def from_id(cls, id):
        return Album.query.get(id)

    @classmethod
    def album_from_title(cls,title):
        return Album.query.filter(Album.title.like(title)).all()

    def get_genres(self):
        res = []
        classifications = Album.query.get(self.id).classifications.all()
        for c in classifications:
            genre = Genre.from_id(c.genre_id) 
            res.append((genre.id,genre.name))
        return res

    def get_genres_id(self):
        genres = Album.get_genres(self)
        res = []
        for g in genres:
            res.append(g[0])
        return res

    def __repr__(self):
        return f"<Album ({self.id}) {self.title}>"

def get_sample_album_without_genre(filter_type, filter_value):
    if filter_type == "title":
        return Album.query.filter(Album.title.like('%'+filter_value+'%')).order_by(Album.title)
    if filter_type == "author":
        return Album.query.join(Artist).filter(Artist.name.like('%'+filter_value+'%')).order_by(Album.title)
    if filter_type == "release":
        try:
            date = int(filter_value)
            return Album.query.filter(Album.release == date).order_by(Album.title)
        except:
            return Album.query.order_by(Album.title).all()
    return Album.query.order_by(Album.title).all()

# **************************************************************************** #
# ******************* gestion relations albums genres ************************ #
# **************************************************************************** #

class Classification(db.Model):
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), primary_key=True)

    album = db.relationship(
        "Album",
        backref=db.backref("classifications", lazy="dynamic"))

    genre = db.relationship(
        "Genre",
        backref=db.backref("classifications", lazy="dynamic"))

    @classmethod
    def create_and_add(cls, album_id, genre_id):
        c = Classification(
            album_id=album_id,
            genre_id=genre_id
        )
        db.session.add(c)
        db.session.commit()
        return c

    @classmethod
    def from_both_ids(cls, album_id, genre_id):
        """
        Get a Classification from its album and genre ids. Return None if the note does not exist.
        """
        req = Classification.query.filter(Classification.album_id==album_id,Classification.genre_id==genre_id).first()
        return req if req else None

    @classmethod
    def delete(cls, album_id, genre_id):
        db.session.delete(Classification.from_both_ids(album_id, genre_id))
        db.session.commit()

# ***************************************************** #
# ************** sécurité des saisies ***************** #
# ***************************************************** #

def secure_filter_genre(filter_genre):
    try :
        filter_g = int(filter_genre)
        genres = get_genres_id()
        if filter_g in genres:
            filter_genre = str(filter_g)
        else:
            filter_genre = ""
        return filter_genre
    except:
        filter_genre = ""
        return filter_genre

def secure_filter_type(filter_type, list_types):
    if filter_type not in list_types:
        filter_type = ""
    return filter_type

def secure_filter_value(filter_value):
    """ cette fonction a pour but de prévenir d'une injection en base de données
    par un utilisateur malvayant

    cette fontione retire: les caractères spéciaux sauf espaces
    et remplace -- par - 

    Args:
        filter_value (string): ce que l'tilisateur souhaite rechercher
    """
    if filter_value == None:
        filter_value = ""
    res = ""
    if len(filter_value) > 0:
        car = filter_value[0]
        for i in range(len(filter_value)):
            if filter_value[i].isalnum():
                res += filter_value[i]
                car = filter_value[i]
            else:
                if not (car == "-" and filter_value[i] == car):
                    if filter_value[i] == " ":
                        res += filter_value[i]
                        car = " "
    return res

def get_sample_album(filter_genre, filter_type, filter_value, lower_limit, upper_limit):

    # ******************************* # 
    #    sécurité sur les filtres     #
    # ******************************* # 

    filter_genre = secure_filter_genre(filter_genre)
    filter_type = secure_filter_type(filter_type,["release","title","author"])
    filter_value = secure_filter_value(filter_value)

    sous_requette = get_sample_album_without_genre(filter_type, filter_value)
    try:
        if filter_genre != "":
            genre_id = int(filter_genre)
            classifications = Genre.query.get(genre_id).classifications.all()
            temp = set()
            for c in classifications:
                album = Album.from_id(c.album_id)
                temp.add(album.id)

            albums=[]
            for album in sous_requette:
                if album.id in temp:
                    albums.append(album)
            return albums[lower_limit:upper_limit]
        else:
            sous_requette[lower_limit:upper_limit]
    except:
        sous_requette[lower_limit:upper_limit]
    return sous_requette[lower_limit:upper_limit]

def get_sample_artist(filter_genre, filter_type, filter_value, lower_limit, upper_limit):

    # ******************************* # 
    #    sécurité sur les filtres     #
    # ******************************* # 

    filter_genre = secure_filter_genre(filter_genre)
    filter_type = secure_filter_type(filter_type,["name"])
    filter_value = secure_filter_value(filter_value)

    sous_requette = get_sample_artist_without_genre(filter_type, filter_value)
    try:
        if filter_genre != "":
            genre_id = int(filter_genre)
            classifications = Genre.query.get(genre_id).classifications.all()
            temp = set()
            for c in classifications:
                artist = Artist.from_id(Album.from_id(c.album_id).artist_id)
                temp.add(artist.id)

            artists=[]
            for artist in sous_requette:
                if artist.id in temp:
                    artists.append(artist)
            return artists[lower_limit:upper_limit]
        else:
            sous_requette[lower_limit:upper_limit]
    except:
        sous_requette[lower_limit:upper_limit]
    return sous_requette[lower_limit:upper_limit]

# **************************************************************************** #
# ************************ gestion des playlists ***************************** #
# **************************************************************************** #

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.username"))

    user = db.relationship(
        "User",
        backref=db.backref("playlists", lazy="dynamic"))

    @classmethod
    def create_and_add(cls, user_id):
        pl = Playlist(user_id=user_id)
        db.session.add(pl)
        db.session.commit()
        return pl

    @classmethod
    def from_id(cls, id):
        return Playlist.query.get_or_404(id)


class Indexation(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"), primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), primary_key=True)

    playlist = db.relationship(
        "Playlist",
        backref=db.backref("indexations", lazy="dynamic"))

    album = db.relationship(
        "Album",
        backref=db.backref("indexations", lazy="dynamic"))

    @classmethod
    def create_and_add(cls, playlist_id, album_id):
        i = Indexation(playlist_id=playlist_id, album_id=album_id)
        db.session.add(i)
        db.session.commit()
        return i


class Notation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.username", primary_key=True))
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), primary_key=True)
    note = db.Column(db.Integer)

    user = db.relationship(
        "User",
        backref=db.backref("notations", lazy="dynamic"))

    album = db.relationship(
        "Album",
        backref=db.backref("notations", lazy="dynamic"))

    @classmethod
    def create_and_add(cls, user_id, album_id, note):
        n = Notation(user_id=user_id, album_id=album_id, note=note)
        db.session.add(n)
        db.session.commit()
        return n

    def __repr__(self):
        return f"<Notation ({self.user_id}, {self.album_id}) {self.note}>"

def get_albums_from_playlist(id_playlist):
    albums = []
    indexations = Playlist.query.get(id_playlist).indexations.all()
    for i in indexations:
        album = Album.query.get(i.album_id)
        albums.append(album)
    return albums


def get_playlists_from_user(user_id):
    return User.query.get(user_id).playlists.all()

# **************************************************************************** #
# *********************** gestion des utilisateurs *************************** #
# **************************************************************************** #

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
        :return: l'utilisateur nouvellement créé
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

@login_manager.user_loader
def load_user(username):
    return User.user_from_username(username)
