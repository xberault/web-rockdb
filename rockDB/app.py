from flask import Flask
from flask_bootstrap import Bootstrap
import os.path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

def mkpath(p):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__),
                     p))


app = Flask(__name__)

Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + mkpath('../myapp.db')
)
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = "23c6b4a9-c635-480e-9b12-2db0b0605fc8"

login_manager = LoginManager(app)
login_manager.login_view = "login"