from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from wtforms.fields.html5 import DateField
from flasksocial.models import User


class Registration(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a different username.")

    def validate_email(self, email):
        user_object = User.query.filter_by(email=email.data).first()
        if user_object:
            raise ValidationError("Email already exists. Select a different email.")


class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class Complete(FlaskForm):
    firstname = StringField('firstname', validators=[InputRequired(message="So you don't have a name?")])
    lastname = StringField('lastname', validators=[InputRequired(message="So you don't have a surname?")])
    date_of_birth = DateField('date_of_birth', format='%Y-%m-%d',
                              validators=[InputRequired(message="Give us a date of birth")])
    submit = SubmitField('Save your data')


class ChangePassword(FlaskForm):
    current_password = PasswordField('current_password_label', validators=[DataRequired()])
    new_password = PasswordField('new_password_label',
                                 validators=[DataRequired(message="Password must be between 4 and 25 characters"),
                                             Length(min=4, max=25)])
    confirm_new_password = PasswordField('confirm_new_password_label',
                                         validators=[DataRequired(message="New password must match"),
                                                     EqualTo('new_password')])
    submit = SubmitField('Change password')


class ChangeName(FlaskForm):
    new_name = StringField('new_name_label', validators=[InputRequired(message="Enter your new name")])
    submit = SubmitField('Change name')


class Post(FlaskForm):
    content = TextAreaField('content', validators=[DataRequired()])
    submit = SubmitField('Share')


class AddFriend(FlaskForm):
    submit = SubmitField('Add Friend')