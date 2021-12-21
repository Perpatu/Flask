import numpy as np

from flask import render_template, redirect, url_for, flash, request, jsonify
from flasksocial import app, db, conn
from flask_login import login_user, logout_user, login_required, current_user
from flasksocial.forms import Registration, Complete, Login, ChangePassword, Post, ChangeName, AddFriend
from flasksocial.models import User, Friedns
from flasksocial import login
from passlib.hash import pbkdf2_sha256
import datetime
import psycopg2
import psycopg2.extras
import os


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
def index():
    if not current_user.is_authenticated:
        reg_form = Registration()
        login_form = Login()
        if reg_form.validate_on_submit():
            hashed_password = pbkdf2_sha256.hash(reg_form.password.data)
            user = User(username=reg_form.username.data, email=reg_form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            os.makedirs('flasksocial/static/users_files/' + str(reg_form.username.data))
            login_user(user)
            return redirect(url_for("complete"))
        elif login_form.validate_on_submit():
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and pbkdf2_sha256.verify(login_form.password.data, user.password):
                login_user(user, remember=login_form.remember.data)
                flash(f'You have been logged in!', 'success')
                return redirect(url_for("content"))
            flash(f'Please check email or password', 'danger')
            return render_template("login.html", form=login_form)
        return render_template("home.html", form_reg=reg_form, form_log=login_form)
    flash(f'You are already logged in!', 'info')
    return redirect(url_for("content"))


@app.route('/complete', methods=["POST", "GET"])
def complete():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    complete_form = Complete()
    if complete_form.validate_on_submit():
        db.session.query(User).filter(User.user_id == current_user.get_id()).update(
            {User.firstname: complete_form.firstname.data}, synchronize_session=False)
        db.session.query(User).filter(User.user_id == current_user.get_id()).update(
            {User.lastname: complete_form.lastname.data}, synchronize_session=False)
        db.session.query(User).filter(User.user_id == current_user.get_id()).update(
            {User.date_of_birth: complete_form.date_of_birth.data}, synchronize_session=False)
        db.session.commit()
        return redirect(url_for("content"))
    return render_template("complete.html", form=complete_form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if not current_user.is_authenticated:
        login_form = Login()
        if login_form.validate_on_submit():
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and pbkdf2_sha256.verify(login_form.password.data, user.password):
                login_user(user, remember=login_form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for("content"))
            flash(f'Please check email or password', 'danger')
        return render_template("login.html", form=login_form)
    flash(f'You are already logged in!', 'info')
    return redirect(url_for("content"))


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    flash(f'You have been logged out!', 'success')
    return redirect(url_for("login"))


@app.route("/content/delete", methods=["GET"])
def delete():
    if current_user.is_authenticated:
        db.session.query(User).filter(User.user_id == current_user.get_id()).delete(synchronize_session=False)
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/content", methods=["POST", "GET"])
def content():

    return render_template("content.html")


@app.route("/ajaxlivesearch", methods=["POST", "GET"])
def ajaxlivesearch():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        if search_word == '':
            query = "SELECT * FROM users ORDER BY user_id"
            cur.execute(query)
            username = cur.fetchall()
        else:
            cur.execute('SELECT * FROM users WHERE username LIKE %(name)s', {'name': '%{}%'.format(search_word)})
            username = cur.fetchall()
    return jsonify({'htmlresponse': render_template('response.html', username=username)})


@app.route("/notifications", methods=["POST", "GET"])
def accept_invite():
    current_user_id = current_user.get_id()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT COUNT(invite) FROM friends WHERE user_id=' + current_user_id)
    result = cur.fetchall()[0][0]
    return jsonify('', render_template('notification_respone.html', notification=result))


@app.route("/settings", methods=["POST", "GET"])
def settings():
    if current_user.is_authenticated:
        change_password_form = ChangePassword()
        change_name_form = ChangeName()
        if change_password_form.validate_on_submit():
            hashed_new_password = pbkdf2_sha256.hash(change_password_form.new_password.data)
            if pbkdf2_sha256.verify(change_password_form.current_password.data,
                                    db.session.query(User).filter_by(user_id=current_user.get_id()).first().password):
                db.session.query(User).filter(User.user_id == current_user.get_id()).update(
                    {User.password: hashed_new_password}, synchronize_session=False)
                db.session.commit()
                logout_user()
                flash(f'Your password has been changed', 'success')
                return redirect(url_for("login"))
            flash(f'Your current password is not correct', 'warning')
            return render_template("settings.html", form=change_password_form, data=db)
        elif change_name_form.validate_on_submit():
            new_firstname = change_name_form.new_name.data
            db.session.query(User).filter(User.user_id == current_user.get_id()).update({User.firstname: new_firstname})
            db.session.commit()
            flash(f'Your name has been changed', 'success')
            return redirect(url_for("settings"))
        return render_template("settings.html", form=change_password_form, form_name=change_name_form, db=db, User=User)
    flash(f'You need to log in', 'warning')
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["POST", "GET"])
def user_profile(username):
    add_friend = AddFriend()
    user = db.session.query(User).filter_by(username=username).first()
    directory_def = os.listdir('flasksocial/static/images/default')
    directory_img = os.listdir('flasksocial/static/users_files')
    img_file = url_for('static', filename='images/profile_picture/' + current_user.image_file)
    current_user_id = current_user.get_id()
    friends_id = user.user_id
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query_empty_check = "SELECT count(*) FROM (SELECT 1 FROM friends LIMIT 1) AS t"
    if add_friend.validate_on_submit():
        time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        send_invite_to_other_user = Friedns(user_id=current_user_id, invite=friends_id, invite_time=time)
        receive_invite_from_user = Friedns(user_id=friends_id, invite=current_user_id, invite_time=time)
        db.session.add(send_invite_to_other_user)
        db.session.add(receive_invite_from_user)
        db.session.commit()
        cur.execute(query_empty_check)
        empty = cur.fetchall()[0][0]
        if empty == 0:
            send_invite_to_other_user = Friedns(user_id=current_user_id, invite=time)
            receive_invite_from_user = Friedns(user_id=friends_id, invite=time)
            db.session.add(send_invite_to_other_user)
            db.session.add(receive_invite_from_user)
            db.session.commit()

        cur.execute('SELECT COUNT(DISTINCT friend_id) FROM friends WHERE user_id=%(current_user_id)s'
                    ' AND friend_id=%(friends_id)s',
                    {'current_user_id': '{}'.format(current_user_id), 'friends_id': '{}'.format(friends_id)})
        query_result = cur.fetchall()
        if query_result[0][0] == 1:
            flash(f'You are already friends', 'info')
            return redirect(url_for('user_profile', username=user.username))
        friend_current_user = Friedns(user_id=current_user_id, friend_id=friends_id)
        friend_other_user = Friedns(user_id=friends_id, friend_id=current_user_id)
        db.session.add(friend_current_user)
        db.session.add(friend_other_user)
        db.session.commit()
    cur.execute('SELECT COUNT(friend_id) FROM friends WHERE user_id=%(friends_id)s',
                {'friends_id': '{}'.format(friends_id)})
    number_of_friends = cur.fetchall()[0][0]
    friends = db.session.query(Friedns).filter_by(user_id=friends_id).all()
    return render_template("profile_user.html", img_file=img_file, directory=directory_def, directory_img=directory_img,
                           user=user, username=username, form=add_friend, number_of_friends=number_of_friends,
                           friends=friends)


@app.route("/profile")
@login_required
def profile():
    if current_user.is_authenticated:
        current_user_id = current_user.get_id()
        user = db.session.query(User).filter_by(user_id=current_user_id).first()
        directory_def = os.listdir('flasksocial/static/images/default')
        directory_img = os.listdir('flasksocial/static/users_files')
        img_file = url_for('static', filename='images/profile_picture/' + current_user.image_file)
    else:
        return redirect(url_for("login"))
    return render_template("personal_profile.html", img_file=img_file, directory=directory_def,
                           directory_img=directory_img, user=user)


"""@app.route("/content")
def post():
    result = db.session.query(User).filter_by(username='perpatu').first()
    return render_template("content.html", result=result)"""
