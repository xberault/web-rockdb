from .app import app
from .forms import LoginForm, SignupForm, ReseachAlbum, ReseachArtist, EditAlbum
from .models import User, get_sample_artist, get_sample_album, get_sample_genre
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, logout_user, current_user, login_user

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
        form = ReseachArtist()
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

    # envoie  de la liste des genre au formulaire
    temp = [(g.id,g.name) for g in get_sample_genre()]
    temp.insert(0,('all','all'))
    form=ReseachAlbum()
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
    return render_template("artist/one_artist.html", title=artist.name, artist=artist)


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
        form = ReseachAlbum()
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

    temp = [(g.id,g.name) for g in get_sample_genre()]
    temp.insert(0,('all','all'))
    form=ReseachAlbum()
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

@app.route("/album/one_album/<int:id>")
def one_album(id):
    album=Album.from_id(id)
    return render_template("album/one_album.html", title=album.title, album = album)

# @login_required
@app.route("/album/edit_and_suppr/<int:id>")
def edit_and_suppr_album(id):
    album=Album.from_id(id)
    test = EditAlbum()
    return render_template("album/edit_and_suppr_album.html",
                           title=album.title,
                           form = test,
                           artist= Artist.from_id(album.artist_id),
                           album = album)

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
@app.route("/playlists/<int:user_id>")
def playlists(user_id):
    return render_template(
        "playlists.html",
        playlists=get_playlists_from_user(user_id)
    )

@app.route("/playlist/<int:id>")
def playlist(id):
    return render_template(
        "playlist.html",
        playlist=Playlist.from_id(id),
        albums=get_albums_from_playlist(id)
    )
