from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from .models import get_sample_genre, get_all_artist
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Length,
                                Optional)


class SignupForm(FlaskForm):
    """User Sign-up Form."""
    name = StringField('Pseudo', validators=[DataRequired()])
    password = PasswordField(
        'Password')
    confirm = PasswordField(
        'Confirmez votre mot de passe'
    )
    submit = SubmitField('Confirmer')


class LoginForm(FlaskForm):
    """User Log-in Form."""
    name = StringField('Pseudo', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Connexion')

class ReseachAlbum(FlaskForm):
    """  """
    gender = SelectField('Gender')
    tipe = SelectField ('By', choices=[('title','Title'),('author','Author'),('release','Released in')])
    value = StringField('value')
    submit = SubmitField('Search')

class ReseachArtist(FlaskForm):
    """  """
    gender = SelectField('Gender')
    tipe = SelectField ('By', choices=[('name','Name')])
    value = StringField('value')
    submit = SubmitField('Search')

class EditAlbum(FlaskForm):
    title = StringField("title")
    release = DateField("Released in",format='%Y')
    img = StringField("Image")
    parent = StringField("Parent")

    # temp = [(g.id,g.name) for g in get_all_artist()]
    # temp.insert(0,('new','New'))
    artist = SelectField("artist",choices=[])
    submit = SubmitField('Sauvegarder')