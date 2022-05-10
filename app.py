import os

from flask import *
from flask import render_template, request
from flask_login import LoginManager
from flask_login import login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm

SECRET_KEY = os.urandom(32)
# FROM_DOMAIN = "statki.pythonanywhere.com"
# TO_DOMAIN = "149.156.43.57/p23"

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://plkpwizjpefcnn:b906d13f6d9fb7ab33551e98f382c97272dc2e3516ef50e420b10eec473ccdef@ec2-99-80-170-190.eu-west-1.compute.amazonaws.com:5432/d1ve7vekfo7818'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


def get_gamers(status=None):
    gamers = Users.query.filter_by(status=status).all()
    return gamers


@app.route('/')
def main_page():
    return render_template('index.html')


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
            return redirect(next or url_for('show_rooms'))
        flash('Nieprawidłowy adres e-mail lub hasło.')
    return render_template('login.html', form=form)


@app.route('/forget')
def forget_password():
    return render_template('forget_password.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.validate_on_submit():
            user = Users(name=form.name.data, email=form.email.data)
            user.set_password(form.password1.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
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

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
# app.run()
