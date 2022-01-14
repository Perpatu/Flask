from flask.helpers import url_for
from flasksocial import mail, app, url_safe
from flask_mail import Message

#<form action=\'{}\'><input type=\'submit\' value=\'activate\'/></form>

class Send():

    @staticmethod
    def confirmation_mail(email, username):

        msg = Message('Hello there (activate link)', recipients=[email])        
        token = url_safe.dumps(email, salt='email-confirm')
        link = url_for('confirm_email', token=token, _external=True)

        msg.html =  "<h2>Confirm your e-mail</h2>" \
                    "<hr>" \
                    "<b style='font-size: large;'>Hello {} in our society!</b>" \
                    "<p>Just clik on the following link to activate your account: <a href='{}' target=\'_blank\'>Click me</a>" \
                    "<p>If it\'s not your email ({}) just delete the messeage.</p>".format(username, link, email)

    

        mail.send(msg)


    @staticmethod
    def invite_mail(email, username, someone):

        msg = Message('Hello there, someone send you invite to friends list', recipients=[email])
        link = url_for('user_profile', username=someone)

        msg.html = "<p>Hello {}, <a href=\'{}\' target=\'_blank\'>user</a> {} wants to be your friend.".format(username, someone, link) 

        mail.send(msg)
