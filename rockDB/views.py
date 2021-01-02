from .app import app
from .forms import LoginForm, SignupForm
from .models import User, get_sample_artist, get_sample_album, get_sample_genre
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, logout_user, current_user, login_user

ITEMS_PER_PAGE = 8

@app.route("/")
def home():
    return render_template(
        "home.html",
        title="RockDB",
        genders = get_sample_genre()
    )


@login_required
@app.route("/dashboard")
def dashboard():
    return render_template(
        'dashboard.html',
        title='Dashboard',
        template='dashboard-page',
        body="Page de profil d'un utilisateur",
        genders = get_sample_genre()
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
        body="Connexion au compte utilisateur",
        genders = get_sample_genre()
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
        body="Inscription d'un utilisateur",
        genders = get_sample_genre()
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


@app.route("/artist")
def all_artist_default():
    return render_template("artist/all_artist.html", test = get_sample_artist(0,ITEMS_PER_PAGE), page_number = 0, genders = get_sample_genre())

@app.route("/artist/<int:page_number>")
def all_artist(page_number):
    if page_number < 0:
        page_number = 0

    lower_limit = page_number * ITEMS_PER_PAGE
    upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
    
    artists = get_sample_artist(lower_limit,upper_limit)

    while len(artists) <= 0:
        if page_number == 0:
            break
        else:
            page_number -= 1
            lower_limit = page_number * ITEMS_PER_PAGE
            upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
            artists = get_sample_artist(lower_limit,upper_limit)

    return render_template("artist/all_artist.html", test = get_sample_artist(lower_limit,upper_limit), page_number = page_number, genders = get_sample_genre())


from .models import Artist


@app.route("/artist/one_artist/<int:id>")
def one_artist(id):
    return render_template("artist/one_artist.html", artist=Artist.from_id(id), genders = get_sample_genre())

@app.route("/album")
def all_album_default():
    return render_template ("album/all_album.html", albums = get_sample_album(0,ITEMS_PER_PAGE), page_number = 0, genders = get_sample_genre())

@app.route("/album/<int:page_number>")
def all_album(page_number):

    if page_number < 0:
        page_number = 0

    lower_limit = page_number * ITEMS_PER_PAGE
    upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
    
    albums = get_sample_album(lower_limit,upper_limit)

    while len(albums) <= 0:
        if page_number == 0:
            break
        else:
            page_number -= 1
            lower_limit = page_number * ITEMS_PER_PAGE
            upper_limit = page_number * ITEMS_PER_PAGE + ITEMS_PER_PAGE
            albums = get_sample_album(lower_limit,upper_limit)
    
    return render_template("album/all_album.html", albums = get_sample_album(lower_limit,upper_limit), page_number = page_number, genders = get_sample_genre())


from .models import Album


@app.route("/album/one_album/<int:id>")
def one_album(id):
    return render_template("album/one_album.html", album=Album.from_id(id), genders = get_sample_genre())


from .models import Playlist, Indexation, get_albums_from_playlist, get_playlists_from_user

@login_required
@app.route("/playlists/<int:user_id>")
def playlists(user_id):
    return render_template(
        "playlists.html",
        playlists=get_playlists_from_user(user_id),
        genders = get_sample_genre()
    )

@app.route("/playlist/<int:id>")
def playlist(id):
    return render_template(
        "playlist.html",
        playlist=Playlist.from_id(id),
        albums=get_albums_from_playlist(id),
        genders = get_sample_genre()
    )
