from flask.helpers import url_for
from flasksocial import mail, app, url_safe
from flask_mail import Message


class Send():

    def confirmation_mail(email, username):

        msg = Message('Hello there (activate link)', recipients=[email])        
        token = url_safe.dumps(email, salt='email-confirm')
        link = url_for('confirm_email', token=token, _external=True)

        msg.html =  "<h2>Confirm your e-mail</h2>" \
                    "<hr>" \
                    "<b style='font-size: large;'>Hello {} in our society!</b>" \
                    "<p>Just clik on the following link to activate your account: {}</p>" \
                    "<p>If it\'s not your email ({}) just delete the messeage.</p>".format(username, link, email)     

        mail.send(msg)


    def invite_mail():
        pass
