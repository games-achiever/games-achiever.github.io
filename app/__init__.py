from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)

# database instance to work locally with
db = SQLAlchemy(app)

# database plugin to migrate changes in schemas and data to server
migrate = Migrate(app, db)

login = LoginManager()
login.init_app(app)
login.login_view = 'login'

from app import models