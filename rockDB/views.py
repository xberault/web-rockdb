from .app import app
from .forms import LoginForm, SignupForm, Reseach, EditAlbum, EditArtist, EditGenre
from .models import User, Classification, get_sample_artist, get_sample_album, get_sample_genre, get_all_artist
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, logout_user, current_user, login_user
import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import os

ITEMS_PER_PAGE = 9
DEFAULT_IMAGE_ALBUM = 'album_vierge.jpeg'
DEFAULT_IMAGE_ARTIST = 'album_vierge.jpeg'


@app.route("/")
def home():
    return render_template(
        "home.html",
        title="RockDB"
    )


# ***************************************************** #
# *********** routes pour les connexions ************** #
# ***************************************************** #

@login_required
@app.route("/dashboard")
def dashboard():
    return render_template(
        'dashboard.html',
        title='Dashboard',
        template='dashboard-page',
        body="Page de profil d'un utilisateur"
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.user_from_username(form.name.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Vous êtes maintenant connecté', 'success')
            return redirect(next_page or url_for('dashboard'))
        flash('Erreur sur le pseudo/mot de passe', 'warning')
        return redirect(url_for('login'))
    return render_template(
        'auth/login.html',
        form=form,
        title='Connexion',
        template='login-page',
        body="Connexion au compte utilisateur"
    )


from .models import load_user
from flask import get_flashed_messages


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    get_flashed_messages()
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = load_user(form.name.data)
        if existing_user:
            flash('Ce pseudo est déjà pris', 'warning')
            return redirect(url_for('signup'))
        elif len(form.password.data) < 6:
            flash('Votre mot de passe doit posséder au moins 6 charactères', 'warning')
            return redirect(url_for('signup'))
        elif form.password.data != form.confirm.data:
            flash('Les mots de pases doivent être identiques', 'warning')
            return redirect(url_for('signup'))
        else:
            u = User.register(form.name.data, form.password.data)
            login_user(u)
            flash("Vous êtes maintenant membre de RockDB", "success")
            return redirect(url_for('dashboard'))
    return render_template(
        'auth/signup.html',
        title='Inscription',
        form=form,
        template='signup-page',
        body="Inscription d'un utilisateur"
    )


@login_required
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    if session.get('was_once_logged_in'):
        # évite d'afficher un message qu'il a déjà eu
        del session['was_once_logged_in']
    flash('Vous êtes maintenant déconnecté', 'success')
    return redirect('/')


# ***************************************************** #
# ************ routes pour les artists **************** #
# ***************************************************** #

def get_list_artists():
    liste = [(art.id, art.name) for art in get_all_artist()]
    liste.insert(0, ('-1', 'new'))
    return liste


def get_list_genres():
    liste = [(g.id, g.name) for g in get_sample_genre()]
    liste.insert(0, ('-1', 'all'))
    return liste


from .models import Artist


@app.route("/artist", methods=['GET', 'POST'])
def all_artist_default():
    return redirect('artist-0')


@app.route("/artist-<int:page_number>", methods=['GET', 'POST'])
def all_artist(page_number):
    # ******************************* #
    #    récupération des données     #
    # ******************************* #

    if request.method == 'POST':
        form = Reseach()
        filter_genre = form.genre.data
        filter_type = form.tipe.data
        filter_value = form.value.data

    elif request.method == 'GET':
        filter_genre = request.args.get('filter_genre')
        filter_type = request.args.get('filter_type')
        filter_value = request.args.get('filter_value')

    # ******************************* #
    # sécurité sur le nombre de pages #
    # ******************************* #

    # pour ne pas aller a la page -1 (ne préviens d'une saisie directe dans l'url)
    if page_number < 0:
        page_number = 0

    # pour ne pas afficher une page vierge
    lower_limit = page_number * ITEMS_PER_PAGE
    upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE

    artists = get_sample_artist(filter_genre, filter_type, filter_value, lower_limit, upper_limit)

    # cette boucle peut etre dangereuse si l'utilisateur malvayant rentre un nombre trop grand
    while len(artists) <= 0:
        if page_number == 0:
            break
        else:
            page_number -= 1
            lower_limit = page_number * ITEMS_PER_PAGE
            upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
            artists = get_sample_artist(filter_genre, filter_type, filter_value, lower_limit, upper_limit)

    form = Reseach()

    # envoie  de la liste des genre au formulaire)
    form.genre.choices = get_list_genres()

    # code pour que la nav bar garde les infos d'une page à l'autre
    try:
        form.genre.default = int(filter_genre)
    except:
        pass
    try:
        form.tipe.default = filter_type
    except:
        pass
    if filter_value != None and filter_value != "":
        form.value.default = filter_value

    form.tipe.choices = [('name', 'Name')]
    form.process()

    return render_template("artist/all_artist.html",
                           title="All artists page " + str(page_number),
                           form=form,
                           dest="all_artist",
                           artists=artists,
                           page_number=page_number,
                           filter_genre=filter_genre,
                           filter_type=filter_type,
                           filter_value=filter_value)


@app.route("/artist/one_artist-<int:id>")
def one_artist(id):
    artist = Artist.from_id(id)
    return render_template("artist/one_artist.html",
                           title=artist.name,
                           artist=artist)


# @login_required
@app.route("/artist/edit-<int:id>", methods=['GET', 'POST'])
def edit_and_suppr_artist(id):
    get_flashed_messages()
    form = EditArtist(CombinedMultiDict((request.files, request.form)))
    artist = Artist.from_id(id)

    if request.method == "POST":

        name = form.name.data
        if artist.name != name:
            existing_artist = Artist.artist_from_name(name) != []
            if existing_artist:
                flash("L'artiste : " + name + " existe déjà", 'warning')

                form.name.default = form.name.data

                return render_template("artist/add_edit_suppr_album.html",
                                       title=artist.name,
                                       form=form,
                                       dest="edit_and_suppr_artist",
                                       id=artist.id)
            else:
                artist.set_name(name)

        flash("Les modifications ont été validées", "success")
        return redirect(url_for('one_artist', id=artist.id))

    if request.method == 'GET':
        # Préremplissage des champs
        form.name.default = artist.name
        form.process()

        return render_template("artist/add_edit_suppr_artist.html",
                               title=artist.name,
                               form=form,
                               dest="edit_and_suppr_artist",
                               id=artist.id)
    flash("Soucis dans la modifiction, retour a la page d'acceil", "warning")
    return redirect('/')


# @login_required
@app.route("/artist/add", methods=['GET', 'POST'])
def add_artist():
    get_flashed_messages()
    form = EditArtist()

    if request.method == "POST":
        name = form.name.data
        existing_artist = Artist.artist_from_name(name) != []
        if existing_artist:
            flash("L'artiste : " + name + " existe déjà", 'warning')
            form.name.default = form.name.data

            return render_template("artist/add_edit_suppr_artist.html",
                                   title="Add Artist",
                                   form=form,
                                   dest="add_artist",
                                   id=-1)

        artist = Artist.create_and_add(name)

        flash("L'artiste a été ajouté avec succès", "success")
        return redirect(url_for('one_artist', id=artist.id))

    if request.method == "GET":
        return render_template("artist/add_edit_suppr_artist.html",
                               title="Add Artist",
                               form=form,
                               dest="add_artist",
                               id=-1)


# @login_required
@app.route("/artist/delete/<int:id>")
def delete_artist(id):
    get_flashed_messages()
    if Artist.from_id(id).name == "Inconnu":
        flash("L'artiste Inconnu ne peut pas être supprimé", "warning")
    else:
        Artist.delete(id)
        flash("L'artiste a été supprimé avec succès", "success")
    return redirect('/artist-0')


# ***************************************************** #
# ************ routes pour les albums ***************** #
# ***************************************************** #

@app.route("/album", methods=['GET', 'POST'])
def all_album_default():
    return redirect('album-0')


@app.route("/album-<int:page_number>", methods=['GET', 'POST'])
def all_album(page_number):
    # ******************************* #
    #    récupération des données     #
    # ******************************* #

    if request.method == 'POST':
        form = Reseach()
        filter_genre = form.genre.data
        filter_type = form.tipe.data
        filter_value = form.value.data

    elif request.method == 'GET':
        filter_genre = request.args.get('filter_genre')
        filter_type = request.args.get('filter_type')
        filter_value = request.args.get('filter_value')

    # ******************************* #
    # sécurité sur le nombre de pages #
    # ******************************* #

    # pour ne pas aller a la page -1 (ne préviens d'une saisie directe dans l'url)
    if page_number < 0:
        page_number = 0

    # pour ne pas afficher une page vierge
    lower_limit = page_number * ITEMS_PER_PAGE
    upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE

    albums = get_sample_album(filter_genre, filter_type, filter_value, lower_limit, upper_limit)

    # cette boucle peut etre dangereuse si l'utilisateur malvayant rentre un nombre trop grand
    while len(albums) <= 0:
        if page_number == 0:
            break
        else:
            page_number -= 1
            lower_limit = page_number * ITEMS_PER_PAGE
            upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
            albums = get_sample_album(filter_genre, filter_type, filter_value, lower_limit, upper_limit)

    form = Reseach()

    form.genre.choices = get_list_genres()

    try:
        form.genre.default = int(filter_genre)
    except:
        pass
    try:
        form.tipe.default = filter_type
    except:
        pass
    if filter_value != None and filter_value != "":
        form.value.default = filter_value

    form.tipe.choices = [('title', 'Title'), ('author', 'Author'), ('release', 'Released in')]
    form.process()

    return render_template("album/all_album.html",
                           title="All albums page " + str(page_number),
                           form=form,
                           dest="all_album",
                           albums=albums,
                           page_number=page_number,
                           filter_genre=filter_genre,
                           filter_type=filter_type,
                           filter_value=filter_value)


from .models import Album


@app.route("/album/one-album-<int:id>", methods=['GET', 'POST'])
def one_album(id):
    album = Album.from_id(id)
    return render_template(
        "album/one_album.html",
        title=album.title,
        album=album
    )


# @login_required
@app.route("/album/edit-<int:id>", methods=['GET', 'POST'])
def edit_and_suppr_album(id):
    get_flashed_messages()
    form = EditAlbum(CombinedMultiDict((request.files, request.form)))
    album = Album.from_id(id)

    if request.method == "POST":

        title = form.title.data
        if album.title != title:
            existing_album = Album.album_from_title(title) != []
            if existing_album:
                flash("L'album : " + title + " existe déjà", 'warning')
                flash("Attention ! Si une image a été upload il faudra la recharger", "warning")

                form.title.default = form.title.data
                form.release.default = form.release.data
                form.img.default = form.img.data
                form.artist.default = form.artist.data
                form.parent.default = form.parent.data

                form.artist.choices = get_list_artists()
                form.parent.choices = get_list_artists()
                form.genres.choices = get_list_genres()

                return render_template("album/add_edit_suppr_album.html",
                                       title=album.title,
                                       form=form,
                                       dest="edit_and_suppr_album",
                                       size=len(form.genres.choices),
                                       id=album.id,
                                       img=album.img)
            else:
                album.set_title(title)

        image = request.files['img']
        if image != None:
            img = image.filename
            if img != "" and img != album.img:
                image.save(
                    os.path.join(os.path.dirname(app.instance_path), 'rockDB/static/images', secure_filename(img)))
                album.set_img(img)

        artist_id = form.artist.data
        if album.artist_id != artist_id:
            if artist_id != -1:
                album.set_artist_id(artist_id)
            else:
                flash("L'ajout d'un nouvel artist depuis un album sera implémenté plus tard", 'warning')

        parent_id = form.parent.data
        if album.parent_id != parent_id:
            if parent_id != -1:
                album.set_parent_id(parent_id)
            else:
                flash("L'ajout d'un nouveau parent depuis un album sera implémenté plus tard", 'warning')

        release = form.release.data.year
        if album.release != release:
            album.set_release(release)

        genres_form = form.genres.data
        genres_album = album.get_genres_id()
        if genres_album != genres_form:
            for genre_id in genres_form:
                genre_id = int(genre_id)
                if genre_id not in genres_album:
                    if genre_id != -1:
                        Classification.create_and_add(album.id, genre_id)
                    else:
                        flash("L'ajout d'un nouveau genre depuis un album sera implémenté plus tard", 'warning')

            # si l'utilisateur supprime des genres 
            for genre_id in genres_album:
                if genre_id not in genres_form:
                    Classification.delete(album.id, genre_id)

        flash("Les modifications ont été validées", "success")
        return redirect(url_for('one_album', id=album.id))

    if request.method == 'GET':

        form.artist.choices = get_list_artists()
        form.parent.choices = get_list_artists()
        form.genres.choices = get_list_genres()

        # Préremplissage des champs
        form.title.default = album.title
        form.parent.default = int(album.parent.id)
        form.artist.default = int(album.artist.id)
        form.release.default = datetime.date(album.release, 1, 1)

        if album.img != None:
            form.img.data = album.img
        else:
            form.img.data = DEFAULT_IMAGE_ALBUM

        form.genres.default = album.get_genres_id()

        form.process()

        return render_template("album/add_edit_suppr_album.html",
                               title=album.title,
                               form=form,
                               dest="edit_and_suppr_album",
                               size=len(form.genres.choices),
                               id=album.id,
                               img=album.img)
    flash("Soucis dans la modifiction, retour a la page d'acceil", "warning")
    return redirect('/')


# @login_required
@app.route("/album/add", methods=['GET', 'POST'])
def add_album():
    get_flashed_messages()
    form = EditAlbum(CombinedMultiDict((request.files, request.form)))

    if request.method == "POST":
        title = form.title.data
        existing_album = Album.album_from_title(title) != []
        if existing_album:
            flash("L'album : " + title + " existe déjà", 'warning')
            form.title.default = form.title.data
            form.release.default = form.release.data
            form.img.default = form.img.data
            form.artist.default = form.artist.data
            form.parent.default = form.parent.data

            form.artist.choices = get_list_artists()
            form.parent.choices = get_list_artists()
            form.genres.choices = get_list_genres()

            flash("Attention ! Si une image a été upload il faudra la recharger", "warning")
            return render_template("album/add_edit_suppr_album.html",
                                   title="Add Album",
                                   form=form,
                                   dest="add_album",
                                   size=len(form.genres.choices),
                                   id=-1,
                                   img=None)

        image = request.files['img']
        if image != None:
            img = image.filename
            if img != "":
                image.save(
                    os.path.join(os.path.dirname(app.instance_path), 'rockDB/static/images', secure_filename(img)))
            else:
                img = DEFAULT_IMAGE_ALBUM
        else:
            img = DEFAULT_IMAGE_ALBUM

        artist_id = form.artist.data
        if artist_id == -1:
            flash("L'ajout d'un nouvel artist depuis un album sera implémenté plus tard", 'warning')

        parent_id = form.parent.data
        if parent_id == -1:
            flash("L'ajout d'un nouveau parent depuis un album sera implémenté plus tard", 'warning')

        release = form.release.data.year

        album = Album.create_and_add(title, release, img, artist_id, parent_id)

        genres_form = form.genres.data
        genres_album = album.get_genres_id()
        if genres_album != genres_form:
            for genre_id in genres_form:
                genre_id = int(genre_id)
                if genre_id not in genres_album:
                    if genre_id != -1:
                        Classification.create_and_add(album.id, genre_id)
                    else:
                        flash("L'ajout d'un nouveau genre depuis un album sera implémenté plus tard", 'warning')

        flash("L'album a été ajouté avec succès", "success")
        return redirect(url_for('one_album', id=album.id))

    if request.method == "GET":
        form.artist.choices = get_list_artists()
        form.parent.choices = get_list_artists()
        form.genres.choices = get_list_genres()

        return render_template("album/add_edit_suppr_album.html",
                               title="Add Album",
                               form=form,
                               dest="add_album",
                               size=len(form.genres.choices),
                               id=-1,
                               img=None)


# @login_required
@app.route("/album/delete-<int:id>")
def delete_album(id):
    get_flashed_messages()

    Album.delete(id)
    flash("L'album a été supprimé avec succès", "success")
    return redirect('/album-0')

# ***************************************************** #
# ***********  routes pour les genres   *************** #
# ***************************************************** #

@app.route("/genre")
def genre ():
    return render_template("genre/genres.html",
                           genres = get_sample_genre())

from .models import Genre

# @login_required
@app.route("/genre/add", methods=['GET', 'POST'])
def add_genre():
    get_flashed_messages()
    form = EditGenre()

    if request.method == "POST":
        name = form.name.data
        existing_genre = Genre.genre_from_name(name) != []
        if existing_genre:
            flash("Le genre: " + name + " existe déjà", 'warning')
            form.name.default = form.name.data
            print("ça passe pas")

            return render_template("genre/add_genre.html",
                                   title="Add Genre",
                                   form=form,
                                   dest="add_genre",
                                   id=-1)

        genre = Genre.create_and_add(name)

        flash("Le genre a été ajouté avec succès", "success")
        return redirect(url_for('genre'))

    if request.method == "GET":
        return render_template("genre/add_genre.html",
                               title="Add Genre",
                               form=form,
                               dest="add_genre",
                               id=-1)

# @login_required
@app.route("/genre/edit-<int:id>", methods=['GET', 'POST'])
def edit_genre(id):
    get_flashed_messages()
    form = EditGenre()
    genre = Genre.from_id(id)

    if request.method == "POST":
        name = form.name.data
        if genre.name != name:
            existing_genre = Genre.genre_from_name(name) != []
            if existing_genre:
                flash("Le genre : "+name+" existe déjà", 'warning')

                form.name.default = form.name.data

                return render_template("genre/add_genre.html",
                                        title = genre.name,
                                        form = form,
                                        dest = "edit_genre",
                                        id = genre.id)
            else:
                genre.set_name(name)

        flash("Les modifications ont été validées", "success")
        return redirect(url_for('genre'))

    if request.method == 'GET':

        # Préremplissage des champs
        form.name.default = genre.name
        form.process()

        return render_template("genre/add_genre.html",
                               title = genre.name,
                               form = form,
                               dest = "edit_genre",
                               id = genre.id)
    flash("Soucis dans la modifiction, retour a la page d'acceil", "warning")
    return redirect('/')

# @login_required
@app.route("/genre/delete-<int:id>")
def delete_genre(id):
    get_flashed_messages()

    Genre.delete(id)
    flash("Le genre a été supprimé avec succès", "success")
    return redirect('/genre')


# ***************************************************** #
# *********** routes pour les playlists *************** #
# ***************************************************** #

from .models import Playlist, Indexation, get_albums_from_playlist, get_playlists_from_user


@login_required
@app.route("/playlist/<string:user_id>")
def playlists(user_id):
    playlists = dict()
    for pl in get_playlists_from_user(user_id):
        playlists[pl] = get_albums_from_playlist(pl.id)

    return render_template(
        "playlist/playlist.html",
        title="Playlists de " + user_id,
        playlists=playlists
    )


@app.route("/one_playlist/<int:id>")
def one_playlist(id):
    return render_template(
        "playlist/one_playlist.html",
        title="Playlist n°" + str(id),
        playlist=Playlist.from_id(id),
        albums=get_albums_from_playlist(id)
    )
