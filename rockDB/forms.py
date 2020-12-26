from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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
