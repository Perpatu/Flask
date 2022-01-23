from flask import render_template, redirect, url_for, flash, request, jsonify
from flasksocial import app, db, conn, login, url_safe, socketio
from flask_login import login_user, logout_user, login_required, current_user
from flasksocial.mail_body import Send 
from flasksocial.forms import Registration, Complete, Login, ChangePassword, PostForm, PostCommentForm, PostCommentDeleteForm, ChangeName, FriendsForm, AcceptFriend
from flasksocial.models import User, Friends, Post, Comment
from itsdangerous import SignatureExpired
from passlib.hash import pbkdf2_sha256
import datetime
import psycopg2
import psycopg2.extras
import os


def send_invite(current_user_id, friends_id):
    time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    send_invite_to_other_user = Friends(user_id=friends_id, invite=current_user_id, invite_time=time)    
    db.session.add(send_invite_to_other_user)    
    db.session.commit()

def confirm():
    if_confirm = db.session.query(User).filter_by(user_id=current_user.get_id()).first().confirm_email
    return if_confirm


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
def index():
    if not current_user.is_authenticated:
        reg_form = Registration()        
        if reg_form.validate_on_submit():
            hashed_password = pbkdf2_sha256.hash(reg_form.password.data)
            user = User(username=reg_form.username.data, email=reg_form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            os.makedirs('flasksocial/static/users_files/' + str(reg_form.username.data))                  
            Send.confirmation_mail(reg_form.email.data, reg_form.username.data)
            login_user(user)
            return redirect(url_for("confirm_wait"))        
        return render_template("home.html", form_reg=reg_form)
    flash(f'You are already logged in!', 'info')
    return redirect(url_for("content"))


@app.route('/confirm_wait')
def confirm_wait():    
    return str(confirm())

@app.route('/confirm_email/<token>')
def confirm_email(token):    
    try:
        url_safe.loads(token, salt='email-confirm', max_age=300)
    except SignatureExpired:
        return "<h1>Token is expired</h1>"
    db.session.query(User).filter_by(user_id=current_user.get_id()).update({User.confirm_email: True}, synchronize_session=False)
    db.session.commit()
    return redirect(url_for("complete"))


@app.route('/complete', methods=["POST", "GET"])
@login_required
def complete():    
    if confirm() == True:
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
    return "Account not active"


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
@login_required
def logout():
    logout_user()
    flash(f'You have been logged out!', 'success')
    return redirect(url_for("login"))


@app.route("/content/delete", methods=["GET"])
@login_required
def delete():
    if current_user.is_authenticated:
        db.session.query(User).filter(User.user_id == current_user.get_id()).delete(synchronize_session=False)
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/content", methods=["POST", "GET"])
@login_required
def content():
    if confirm() == True:
        post_form = PostForm()
        comment_form = PostCommentForm()
        delete_comment_form = PostCommentDeleteForm()           
        current_user_id = current_user.get_id()
        friends = db.session.query(Friends).filter_by(user_id=current_user_id).all()   
        try:
            posts = db.session.query(Post)
            comments = db.session.query(Comment)        
        except:
            pass            
        if post_form.submit_post.data and post_form.validate():
            post = Post(content=post_form.content.data, user_id=current_user_id)            
            db.session.add(post)
            db.session.commit()                      
            flash('Your post has been created!', 'success')
            return redirect(url_for('content'))            
        elif comment_form.content_comment.data and comment_form.validate():
            post_id = int(request.form['post_id'])            
            comment = Comment(post_id=post_id, user_id=current_user_id, comment_content=comment_form.content_comment.data)
            db.session.add(comment)
            db.session.commit()
            quantity_of_comments = db.session.query(Post).filter_by(post_id=post_id).first().quantity_of_comments           
            quantity_of_comments += 1
            db.session.query(Post).filter_by(post_id=post_id).update({Post.quantity_of_comments: quantity_of_comments}, synchronize_session=False)
            db.session.commit()
            return redirect(url_for('content'))         
        elif delete_comment_form.submit_delete.data and delete_comment_form.validate():
            comment_id = int(request.form['comment_id'])
            post_id = int(request.form['post_id'])
            db.session.query(Comment).filter_by(comment_id=comment_id).delete()
            db.session.commit()
            quantity_of_comments = db.session.query(Post).filter_by(post_id=post_id).first().quantity_of_comments           
            quantity_of_comments -= 1
            db.session.query(Post).filter_by(post_id=post_id).update({Post.quantity_of_comments: quantity_of_comments}, synchronize_session=False)
            db.session.commit()
            return redirect(url_for('content'))            
        return render_template("content.html", post_form=post_form, comment_form=comment_form, delete_comment_form=delete_comment_form, posts=posts,
                                               comments=comments, friends=friends, current_user_id=int(current_user_id), now=datetime.datetime.utcnow())
    return "Account not active"


@app.route("/settings", methods=["POST", "GET"])
@login_required
def settings():
    if confirm() == True:
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
    return "Account not active"


@app.route("/profile/<username>", methods=["POST", "GET"])
@login_required
def user_profile(username):
    if confirm() == True:
        friend_form = FriendsForm()
        user = db.session.query(User).filter_by(username=username).first()
        directory_def = os.listdir('flasksocial/static/images/default')
        directory_img = os.listdir('flasksocial/static/users_files')
        img_file = url_for('static', filename='images/profile_picture/' + current_user.image_file)
        current_user_id = current_user.get_id()
        friend_id = user.user_id
        friends = db.session.query(Friends).filter_by(user_id=friend_id).all()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute('SELECT COUNT(friend_id) FROM friends WHERE friend_id=%(friends_id)s',
                    {'friends_id': '{}'.format(friend_id)})
        number_of_friends = cur.fetchall()[0][0]

        cur.execute('SELECT COUNT(DISTINCT friend_id) FROM friends WHERE user_id=%(current_user_id)s'
                    ' AND friend_id=%(friend_id)s',
                    {'current_user_id': '{}'.format(current_user_id), 'friend_id': '{}'.format(friend_id)})
        friend_chcek = cur.fetchall()[0][0]

        cur.execute('SELECT COUNT(DISTINCT invite) FROM friends WHERE user_id=%(current_user_id)s'
                    ' AND invite=%(invite)s',
                    {'current_user_id': '{}'.format(friend_id), 'invite': '{}'.format(current_user_id)})
        invite_chcek = cur.fetchall()[0][0]

        cur.execute("SELECT count(*) FROM (SELECT 1 FROM friends LIMIT 1) AS t")
        empty = cur.fetchall()[0][0]
        
        print("current_user_id: ", current_user_id)
        print("friend_id: ", friend_id)

        if friend_form.validate_on_submit():
            if friend_form.invite.data:
                if empty == 0:
                    send_invite(current_user_id, friend_id)
                else:                
                    if invite_chcek == 1:
                        flash(f'You are already send invite to {username}', 'info')
                    elif friend_chcek == 1:
                        flash(f'You are already friends with {username}', 'info')
                    elif (invite_chcek + friend_chcek) == 0: 
                        send_invite(current_user_id, friend_id)                        
                return redirect(url_for('user_profile', username=user.username))
            elif friend_form.delete.data:                
                db.session.query(Friends).filter_by(user_id=current_user_id, friend_id=friend_id).delete()
                db.session.query(Friends).filter_by(user_id=friend_id, friend_id=current_user_id).delete()
                db.session.commit()
                flash(f'You are deleted {username} from friends list', 'info')
                return redirect(url_for('user_profile', username=user.username))
        return render_template("profile_user.html", img_file=img_file, directory=directory_def, directory_img=directory_img,
                            user=user, username=username, form=friend_form, number_of_friends=number_of_friends,
                            friends=friends, friend_chcek=friend_chcek)
    return "Account not active"


@app.route("/profile")
@login_required
def profile():
    if confirm() == True:
        if current_user.is_authenticated:
            directory_def = os.listdir('flasksocial/static/images/default')
            directory_img = os.listdir('flasksocial/static/users_files')
            img_file = url_for('static', filename='images/profile_picture/' + current_user.image_file)
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            current_user_id = current_user.get_id()
            user = db.session.query(User).filter_by(user_id=current_user_id).first()
            cur.execute('SELECT COUNT(friend_id) FROM friends WHERE user_id=%(friends_id)s',
                        {'friends_id': '{}'.format(current_user_id)})
            number_of_friends = cur.fetchall()[0][0]
            friends = db.session.query(Friends).filter_by(user_id=current_user_id).all()        
        else:
            return redirect(url_for("login"))
        return render_template("personal_profile.html", img_file=img_file, directory=directory_def,
                            directory_img=directory_img, user=user, friends=friends, number_of_friends=number_of_friends)
    return "Account not active"


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
def notifications():
    current_user_id = current_user.get_id()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT COUNT(invite) FROM friends WHERE user_id=' + current_user_id)
    number_of_notifications = cur.fetchall()[0][0]  
    return jsonify(number_of_notifications)


@app.route("/accept_invite", methods=["POST", "GET"])
def accept_invite():
    accept_friend_form = AcceptFriend()   
    current_user_id = current_user.get_id()
    user = db.session.query(User)    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    cur.execute('SELECT invite FROM friends WHERE user_id=' + current_user_id)
    users_inivites = cur.fetchall()    
    if accept_friend_form.validate_on_submit():        
        if accept_friend_form.accept.data:
            invite_id = int(request.form['accept_inv'])
            cos = db.session.query(Friends).filter_by(user_id=current_user_id).all()  
            for user_invitation in cos:
                if user_invitation.invite == invite_id:      
                    db.session.query(Friends).filter_by(user_id=current_user_id, invite=user_invitation.invite).update({Friends.friend_id:
                    user_invitation.invite}, synchronize_session=False)
                    db.session.query(Friends).filter_by(user_id=current_user_id, invite=user_invitation.invite).update({Friends.invite_time:
                    None}, synchronize_session=False)
                    db.session.query(Friends).filter_by(user_id=current_user_id, invite=user_invitation.invite).update({Friends.invite:
                    None}, synchronize_session=False)
                    db.session.add(Friends(user_id=user_invitation.invite, friend_id=current_user_id))
                    db.session.commit()                    
        elif accept_friend_form.discard.data:
            invite_id = int(request.form['discard_inv'])
            cos = db.session.query(Friends).filter_by(user_id=current_user_id).all()  
            for user_invitation in cos:
                if user_invitation.invite == invite_id:                    
                    db.session.query(Friends).filter_by(user_id=current_user_id, invite=user_invitation.invite).delete()
                    db.session.commit()                        
        return redirect(url_for("profile"))       
    return jsonify({'htmlresponse': render_template('accept_invite.html', db=db, user=user, users_inivites=users_inivites,
                                                                          accept_form=accept_friend_form)})

@app.route('/test')
def test():
    Send.confirmation_mail('perpatussss@gmail.com', 'ktos')
    return 'cos'
