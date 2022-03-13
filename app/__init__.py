from flask import Flask
from flask_login import LoginManager
from app.commands import add_user, create_tables, create_test_tables
import app.config as config

from app.extentions import db, login_manager

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

login = LoginManager(app)
login.login_view = 'login'

app.cli.add_command(add_user)
app.cli.add_command(create_tables)
app.cli.add_command(create_test_tables)

from app import routes, models
