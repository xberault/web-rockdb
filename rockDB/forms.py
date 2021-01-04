from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from .models import get_sample_genre
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
    temp = [(g.id,g.name) for g in get_sample_genre()]
    temp.insert(0,('all','all'))
    gender = SelectField('Gender',choices=temp)
    tipe = SelectField ('By', choices=[('title','Title'),('author','Author'),('release','Released in')])
    value = StringField('value')
    submit = SubmitField('Search')

class ReseachArtist(FlaskForm):
    """  """
    temp = [(g.id,g.name) for g in get_sample_genre()]
    temp.insert(0,('all','all'))
    gender = SelectField('Gender',choices=temp)
    tipe = SelectField ('By', choices=[('name','Name')])
    value = StringField('value')
    submit = SubmitField('Search')
