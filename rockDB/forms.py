from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, SelectMultipleField, FileField
from .models import get_sample_genre, get_all_artist
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Length,
                                Optional,
                                Regexp,
                                URL)


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

class Reseach(FlaskForm):
    """  """
    gender = SelectField('Gender')
    tipe = SelectField ('By', choices=[])
    value = StringField('value')
    submit = SubmitField('Search')

class EditAlbum(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    release = DateField("Released_in",format='%Y', validators=[DataRequired()])
    img = FileField("Image")
    parent = SelectField("Parent", coerce=int,choices=[], validators=[DataRequired()])
    artist = SelectField("Artist", coerce=int,choices=[], validators=[DataRequired()])
    genders = SelectMultipleField("Genders", coerce=int, choices=[], validators=[DataRequired()])
    submit = SubmitField('Sauvegarder')