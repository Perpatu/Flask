from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
import psycopg2.extras


app = Flask(__name__)
app.config['SECRET_KEY'] = '53b2cdd9a055e2a6f6fd82e61067c6ea'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://njkjgxoxjmyvtk:81e33a32ec010d5743aedf2c7cedf8c312408eaeb9a96063c0c6667dec6f63a4@ec2-54-163-97-228.compute-1.amazonaws.com:5432/d6dsehs7hroh07'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'
login.login_message_category = 'info'
DB_HOST = "ec2-54-163-97-228.compute-1.amazonaws.com"
DB_NAME = "d6dsehs7hroh07"
DB_USER = "njkjgxoxjmyvtk"
DB_PASS = "81e33a32ec010d5743aedf2c7cedf8c312408eaeb9a96063c0c6667dec6f63a4"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
#app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'perpatussss@gmail.com'
app.config['MAIL_PASSWORD'] = 'MG99100507139!!!!pl'
app.config['MAIL_DEFAULT_SENDER'] = ('Perpatu from Society', 'perpatussss@gmail.com')
app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

url_safe = URLSafeTimedSerializer(app.config['SECRET_KEY'])

from flasksocial import routes
