from flask_login import UserMixin
from flasksocial import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    firstname = db.Column(db.String(100), nullable=False, default="")
    lastname = db.Column(db.String(100), nullable=False, default="")
    date_of_birth = db.Column(db.String(30), nullable=False, default="")
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.firstname}', '{self.lastname}', {self.user_id})"


class Friends(db.Model):
    __tablename__ = 'friends'
    friends_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer())
    friend_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    invite = db.Column(db.Integer())
    invite_time = db.Column(db.String(30))
    user = db.relationship('User', backref='author', lazy=True)

    def __repr__(self):
        return f"Friend('{self.user_id}', '{self.friend_id}', {self.user}, {self.invite})"


"""class Post(db.Model):
    __tablename__ = 'posts'
    PostID = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow())
    content = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.content}', '{self.date_posted}')"""
