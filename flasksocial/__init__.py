from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import psycopg2.extras

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'
login.login_message_category = 'info'
DB_HOST = ""
DB_NAME = ""
DB_USER = ""
DB_PASS = ""
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

from flasksocial import routes

