import os
import random
import string
from flask import *
from flask import render_template, request
from forms import LoginForm, RegistrationForm, ResetPasswordForm
from flask_mail import Mail, Message

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pusher import pusher

SECRET_KEY = os.urandom(32)
# FROM_DOMAIN = "statki.pythonanywhere.com"
# TO_DOMAIN = "149.156.43.57/p23"

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://qbhjnrrwqvchoi:a12038c8f5d69267b00001db8cd0762c79458d0ec0cf8399467df7e04d1d8d50@ec2-34-242-8-97.eu-west-1.compute.amazonaws.com:5432/d9qk23pnab16ud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

# do wysyłania maili
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "shipgamesender@gmail.com"
app.config['MAIL_PASSWORD'] = "okretyOkrety2"
mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

pusher = pusher_client = pusher.Pusher(
    app_id='1410664',
    key='4d2726b6eaed69e2834f',
    secret='3ca2a9d952ba6921320b',
    cluster='eu',
    ssl=True
)
name = ''


def password_generator(len_of_password):
    length = len_of_password

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits

    all = lower + upper + num
    temp = random.sample(all, length)
    password = "".join(temp)

    return password


def get_gamers(status=None):
    gamers = Users.query.filter_by(status=status).all()
    return gamers


@app.route('/')
def main_page():
    return render_template('index.html')


@login_required
@app.route('/play')
def play():
    return render_template('play.html', name=current_user.name)


@app.route("/pusher/auth", methods=['POST'])
def pusher_authentication():
    auth = pusher.authenticate(
        channel=request.form['channel_name'],
        socket_id=request.form['socket_id'],
        custom_data={
            u'user_id': name,
            u'user_info': {
                u'role': u'player'
            }
        }
    )
    return json.dumps(auth)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route('/profile')
def profile():
    return render_template('profile.html')


@login_required
@app.route('/rooms')
def show_rooms():
    return render_template('rooms.html',
                           users=get_gamers(),
                           available=get_gamers('available'),
                           in_game=get_gamers('in_game'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for('play'))
        flash('Nieprawidłowy adres e-mail lub hasło.')
    return render_template('login.html', form=form)


@app.route('/forget', methods=['GET', 'POST'])
def forget_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():

        user = Users.query.filter_by(email=form.email.data).first()
        new_password = password_generator(10)
        if user is not None:
            # tu wysyłamy maila
            msg = Message()
            msg.subject = "Reset Password mail"
            msg.recipients = [form.email.data]
            msg.sender = 'shipgamesender@gmail.com'
            msg.body = f"Twoje nowe hasło to: {new_password}"
            mail.send(msg)

            # tu zmieniamy hasło w bazie
            user = Users.query.filter_by(email=form.email.data).first()
            # user.password = new_password
            user.set_password(new_password)
            db.session.commit()
            flash(f"Wysłano mail na adres: {form.email.data}")
            return redirect(url_for('login'))
        flash('Użytkownik o takiem adresie mail nie istnieje')
    return render_template('forget_password.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.validate_on_submit():
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:
                user = Users(name=form.name.data, email=form.email.data)
                user.set_password(form.password1.data)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            flash('Użytkownik o takiem adresie mail już istnieje')
    return render_template('register.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


# @app.before_request
# def redirect_to_new_domain():
#     urlparts = urlparse(request.url)
#     if urlparts.netloc == FROM_DOMAIN:
#         urlparts_list = list(urlparts)
#         urlparts_list[1] = TO_DOMAIN
#     return redirect(urlunparse(urlparts_list), code=301)


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(150), unique=True, index=True)
    password = db.Column(db.String(150))
    status = db.Column(db.String(150))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


if __name__ == "__main__":
    app.debug = True
    app.run()
