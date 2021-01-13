from .app import app
from .forms import LoginForm, SignupForm, Reseach, EditAlbum
from .models import User, Classification, get_sample_artist, get_sample_album, get_sample_genre, get_all_artist
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, logout_user, current_user, login_user
import datetime

ITEMS_PER_PAGE = 8

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

from .models import Artist

@app.route("/artist", methods=['GET', 'POST'])
def all_artist_default():
    return redirect('artist/0')

@app.route("/artist/<int:page_number>", methods=['GET', 'POST'])
def all_artist(page_number):

    # ******************************* #
    #    récupération des données     #
    # ******************************* #

    if request.method == 'POST':
        form = Reseach()
        filter_gender = form.gender.data
        filter_type = form.tipe.data
        filter_value = form.value.data

    elif request.method == 'GET':
        filter_gender = request.args.get('filter_gender')
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

    artists = get_sample_artist(filter_gender, filter_type, filter_value, lower_limit, upper_limit)

    # cette boucle peut etre dangereuse si l'utilisateur malvayant rentre un nombre trop grand
    while len(artists) <= 0:
        if page_number == 0:
            break
        else:
            page_number -= 1
            lower_limit = page_number * ITEMS_PER_PAGE
            upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
            artists = get_sample_artist(filter_gender, filter_type, filter_value, lower_limit, upper_limit)

    form=Reseach()

    # envoie  de la liste des genre au formulaire
    temp = [(g.id,g.name) for g in get_sample_genre()]
    temp.insert(0,('all','all'))
    form.gender.choices=temp

    # code pour que la nav bar garde les infos d'une page à l'autre
    try:
        form.gender.default = int(filter_gender)
    except:
        pass
    try:
        form.tipe.default = filter_type
    except:
        pass
    if filter_value != None and filter_value != "":
        form.value.default = filter_value
    
    form.tipe.choices = [('name','Name')]
    form.process()

    return render_template("artist/all_artist.html",
                           title = "All artists page "+str(page_number),
                           form = form,
                           dest = "all_artist",
                           artists = artists,
                           page_number = page_number,
                           filter_gender = filter_gender,
                           filter_type = filter_type,
                           filter_value = filter_value)


@app.route("/artist/one_artist/<int:id>")
def one_artist(id):
    artist=Artist.from_id(id)
    return render_template(
        "artist/one_artist.html",
        title=artist.name,
        artist=artist
    )


# ***************************************************** #
# ************ routes pour les albums ***************** #
# ***************************************************** #

@app.route("/album", methods=['GET', 'POST'])
def all_album_default():
    return redirect('album/0')

@app.route("/album/<int:page_number>", methods=['GET', 'POST'])
def all_album(page_number):

    # ******************************* #
    #    récupération des données     #
    # ******************************* #

    if request.method == 'POST':
        form = Reseach()
        filter_gender = form.gender.data
        filter_type = form.tipe.data
        filter_value = form.value.data

    elif request.method == 'GET':
        filter_gender = request.args.get('filter_gender')
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

    albums = get_sample_album(filter_gender, filter_type, filter_value, lower_limit, upper_limit)

    # cette boucle peut etre dangereuse si l'utilisateur malvayant rentre un nombre trop grand
    while len(albums) <= 0:
        if page_number == 0:
            break
        else:
            page_number -= 1
            lower_limit = page_number * ITEMS_PER_PAGE
            upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
            albums = get_sample_album(filter_gender, filter_type, filter_value, lower_limit, upper_limit)

    form=Reseach()

    temp = [(g.id,g.name) for g in get_sample_genre()]
    temp.insert(0,('all','all'))
    form.gender.choices=temp

    try:
        form.gender.default = int(filter_gender)
    except:
        pass
    try:
        form.tipe.default = filter_type
    except:
        pass
    if filter_value != None and filter_value != "":
        form.value.default = filter_value

    form.tipe.choices = [('title','Title'),('author','Author'),('release','Released in')]
    form.process()

    return render_template("album/all_album.html",
                           title = "All albums page "+str(page_number),
                           form = form,
                           dest = "all_album",
                           albums = albums,
                           page_number = page_number,
                           filter_gender = filter_gender,
                           filter_type = filter_type,
                           filter_value = filter_value)


from .models import Album

@app.route("/album/one-album-<int:id>", methods=['GET', 'POST'])
def one_album(id):
    album=Album.from_id(id)
    return render_template(
        "album/one_album.html",
        title=album.title,
        album = album
    )

# @login_required
@app.route("/album/edit/<int:id>", methods=['GET', 'POST'])
def edit_and_suppr_album(id):
    get_flashed_messages()
    form = EditAlbum()
    album=Album.from_id(id)

    if request.method == "POST":

        title = form.title.data
        if album.title != title:
            existing_album = Album.album_from_title(title) != None
            if existing_album:
                flash("l'album : "+title+" existe déjà", 'warning')
                return redirect('/album/edit/'+str(id))
            else:
                album.set_title(title)

        img = form.img.data
        if album.img != img:
            album.set_img(img)
        
        artist_id = form.artist.data
        if album.artist_id != artist_id:
            if artist_id != "new":
                album.set_artist_id(artist_id)
            else:
                flash("'ajout d'un nouvel artist depuis un album sera implémenté plus tard", 'warning')
        
        parent_id = form.parent.data
        if album.parent_id != parent_id:
            if parent_id != "new":
                album.set_parent_id(parent_id)
            else:
                flash("L'ajout d'un nouveau parent depuis un album sera implémenté plus tard", 'warning')

        release = form.release.data.year
        if album.release != release:
            album.set_release(release)
        
        genders_form = form.genders.data
        genders_album = album.get_genres_id()
        print('liste via form', genders_form)
        print('liste via album', genders_album)
        if genders_album != genders_form:
            for gender_id in genders_form:
                gender_id = int(gender_id)
                if gender_id not in genders_album:
                    print("possible ajout de", gender_id)
                    if gender_id != "new":
                        Classification.create_and_add(album.id, gender_id)
                    else:
                        flash("L'ajout d'un nouveau genre depuis un album sera implémenté plus tard", 'warning')
            
            # si l'utilisateur supprime des genres 
            for gender_id in genders_album:
                temp = str(gender_id)
                if temp not in genders_form:
                    Classification.delete(album.id,gender_id)

        flash("Les modifications ont été validées", "success")
        return redirect(url_for('one_album',id=album.id))

    if request.method == 'GET':

        temp = [(art.id,art.name) for art in get_all_artist()]
        temp.insert(0,('new','new'))
        form.artist.choices = temp
        form.parent.choices = temp

        genders = [(g.id,g.name) for g in get_sample_genre()]
        genders.insert(0,('new','new'))
        form.genders.choices = genders

        # Préremplissage des champs
        form.title.default = album.title
        form.parent.default = int(album.parent.id)
        form.artist.default = int(album.artist.id)
        form.release.default = datetime.date(album.release,1,1)
        form.img.default = album.img

        form.genders.default = album.get_genres_id()

        form.process()

        return render_template("album/add_edit_suppr_album.html",
                            title = album.title,
                            form = form,
                            dest = "edit_and_suppr_album",
                            size = len(genders),
                            album = album)
    flash("Soucis dans la modifiction, retour a la page d'acceil", "warning")
    return redirect('/')

# @login_required
@app.route("/album/add-album")
def add_album():
    get_flashed_messages()
    form = EditAlbum()

    if request.method == "POST":
        pass

    if request.method == "GET":
        temp = [(art.id,art.name) for art in get_all_artist()]
        temp.insert(0,('new','new'))
        form.artist.choices = temp
        form.parent.choices = temp

        genders = [(g.id,g.name) for g in get_sample_genre()]
        genders.insert(0,('new','new'))
        form.genders.choices = genders

        return render_template("album/add_edit_suppr_album.html",
                                title = "Add Album",
                                form = form,
                                dest = "add_album",
                                size = len(genders),
                                album = Album.from_id(1))

# @login_required
@app.route("/album/delete/<int:id>")
def delete_album(id):
    Album.delete(id)
    return redirect('/album/0')


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
        title="Playlists de "+user_id,
        playlists=playlists
    )

@app.route("/one_playlist/<int:id>")
def one_playlist(id):
    return render_template(
        "playlist/one_playlist.html",
        title="Playlist n°"+str(id),
        playlist=Playlist.from_id(id),
        albums=get_albums_from_playlist(id)
    )
