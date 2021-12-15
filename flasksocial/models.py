from datetime import datetime
from flask_login import UserMixin
from flasksocial import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(), nullable=False, default="")
    lastname = db.Column(db.String(), nullable=False, default="")
    date_of_birth = db.Column(db.String(), nullable=False, default="")
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    friends = db.Column(db.String(50), nullable=False, default="")
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    __tablename__ = 'posts'
    PostID = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow())
    content = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.content}', '{self.date_posted}')"
