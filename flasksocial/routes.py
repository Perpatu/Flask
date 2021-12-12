from flask import render_template, redirect, url_for, flash, request, jsonify
from flasksocial import app, db
from flask_login import login_user, logout_user, login_required, current_user
from flasksocial.forms import Registration, Complete, Login, ChangePassword, Post, ChangeName
from flasksocial.models import User
from flasksocial import login
from passlib.hash import pbkdf2_sha256
import psycopg2
import psycopg2.extras
import os

DB_HOST = "ec2-54-163-97-228.compute-1.amazonaws.com"
DB_NAME = "d6dsehs7hroh07"
DB_USER = "njkjgxoxjmyvtk"
DB_PASS = "81e33a32ec010d5743aedf2c7cedf8c312408eaeb9a96063c0c6667dec6f63a4"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


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
            os.makedirs('flasksocial\\static\\images\\users_files\\' + str(reg_form.username.data))
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
        db.session.query(User).filter(User.id == current_user.get_id()).update(
            {User.firstname: complete_form.firstname.data}, synchronize_session=False)
        db.session.query(User).filter(User.id == current_user.get_id()).update(
            {User.lastname: complete_form.lastname.data}, synchronize_session=False)
        db.session.query(User).filter(User.id == current_user.get_id()).update(
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
        db.session.query(User).filter(User.id == current_user.get_id()).delete(synchronize_session=False)
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/content", methods=["POST", "GET"])
def content():
    return render_template("content.html")


@app.route("/ajaxlivesearch",methods=["POST","GET"])
def ajaxlivesearch():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        if search_word == '':
            query = "SELECT * from users ORDER BY id"
            cur.execute(query)
            username = cur.fetchall()
        else:
            cur.execute('SELECT * FROM users WHERE username LIKE %(name)s', { 'name': '%{}%'.format(search_word)})
            username = cur.fetchall()
            asd = request.args
    return jsonify({'htmlresponse': render_template('response.html', username=username)})


@app.route("/settings", methods=["POST", "GET"])
def settings():
    if current_user.is_authenticated:
        change_password_form = ChangePassword()
        change_name_form = ChangeName()
        if change_password_form.validate_on_submit():
            hashed_new_password = pbkdf2_sha256.hash(change_password_form.new_password.data)
            if pbkdf2_sha256.verify(change_password_form.current_password.data,
                                    db.session.query(User).filter_by(id=current_user.get_id()).first().password):
                db.session.query(User).filter(User.id == current_user.get_id()).update(
                    {User.password: hashed_new_password}, synchronize_session=False)
                db.session.commit()
                logout_user()
                flash(f'Your password has been changed', 'success')
                return redirect(url_for("login"))
            flash(f'Your current password is not correct', 'warning')
            return render_template("settings.html", form=change_password_form, data=db)
        elif change_name_form.validate_on_submit():
            new_firstname = change_name_form.new_name.data
            db.session.query(User).filter(User.id == current_user.get_id()).update({User.firstname: new_firstname})
            db.session.commit()
            flash(f'Your name has been changed', 'success')
            return redirect(url_for("settings"))
        return render_template("settings.html", form=change_password_form, form_name=change_name_form, db=db, User=User)
    flash(f'You need to log in', 'warning')
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    directory_def = os.listdir('flasksocial/static/images/default')
    directory_img = os.listdir('flasksocial/static/images/users_files')
    img_file = url_for('static', filename='images/profile_picture/' + current_user.image_file)
    return render_template("profile.html", img_file=img_file, directory=directory_def, directory_img=directory_img)


@app.route("/search/<username>")
def user_profile(username):
    asd = request.form.get("search_text")
    user = db.session.query(User).filter_by(username=username).first()
    directory_def = os.listdir('flasksocial/static/images/default')
    directory_img = os.listdir('flasksocial/static/images/users_files')
    img_file = url_for('static', filename='images/profile_picture/' + current_user.image_file)
    return render_template("search.html", img_file=img_file, directory=directory_def, directory_img=directory_img, user=user, username1=username)

@app.route("/test",  methods=["POST", "GET"])
def test():
    asd = request.form.get("search_text")
    return render_template("search.html", asd="asd")


"""@app.route("/search/<username>", methods=["POST", "GET"])
def search(username):
    if request.method == "POST":
        form = request.form
        search_value = form['search_string'] = username
        search = "%{0}%".format(search_value)
        results = User.query.filter(User.username.like(search)).all()

        return render_template("/search.html", results=results)
    else:
        return redirect('/')"""


@app.route("/content")
def post():
    result = db.session.query(User).filter_by(username='perpatu').first()
    return render_template("content.html", result=result)
