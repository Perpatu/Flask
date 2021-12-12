from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = '53b2cdd9a055e2a6f6fd82e61067c6ea'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://njkjgxoxjmyvtk:81e33a32ec010d5743aedf2c7cedf8c312408eaeb9a96063c0c6667dec6f63a4@ec2-54-163-97-228.compute-1.amazonaws.com:5432/d6dsehs7hroh07'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'
login.login_message_category = 'info'



from flasksocial import routes

