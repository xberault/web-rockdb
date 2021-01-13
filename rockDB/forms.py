from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, SelectMultipleField
from .models import get_sample_genre, get_all_artist
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Length,
                                Optional,
                                InputRequired,
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
    title = StringField("Title", validators=[Optional()])
    release = DateField("Released_in",format='%Y', validators=[Optional()])
    img = StringField("Image", validators=[Optional()])
    parent = SelectField("Parent",choices=[], validators=[Optional()])
    artist = SelectField("Artist",choices=[], validators=[Optional()])
    genders = SelectMultipleField("Genders",choices=[], validators=[Optional()])
    submit = SubmitField('Sauvegarder')