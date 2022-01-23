from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO
from itsdangerous import URLSafeTimedSerializer
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


app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = ''
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
#app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''
app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

url_safe = URLSafeTimedSerializer(app.config['SECRET_KEY'])

socketio = SocketIO(app)


from flasksocial import routes
