import os
import random
import string
from flask import *
from flask import render_template, request
from sqlalchemy import text

from forms import LoginForm, RegistrationForm, ResetPasswordForm
from flask_mail import Mail, Message
from flask_cors import CORS

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pusher import pusher
from enum import Enum

SECRET_KEY = os.urandom(32)
# FROM_DOMAIN = "statki.pythonanywhere.com"
# TO_DOMAIN = "149.156.43.57/p23"

app = Flask(__name__)

pusher = pusher_client = pusher.Pusher(
    app_id='1410664',
    key='4d2726b6eaed69e2834f',
    secret='3ca2a9d952ba6921320b',
    cluster='eu',
    ssl=True
)
name = ''
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://qbhjnrrwqvchoi:a12038c8f5d69267b00001db8cd0762c79458d0ec0cf8399467df7e04d1d8d50@ec2-34-242-8-97.eu-west-1.compute.amazonaws.com:5432/d9qk23pnab16ud'

# app.config[
#     'SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:1234@localhost:5432/postgres'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)

# do wysyłania maili
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "shipgamesender@gmail.com"
app.config['MAIL_PASSWORD'] = "sjripnmdztjsrvoc"
mail = Mail(app)

db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(150), unique=True, index=True)
    password = db.Column(db.String(150))
    status = db.Column(db.String(150))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.name


class GameResult(Enum):
    WON = 1
    LOST = 2
    NOT_CONCLUDED = 0


class GameState(Enum):
    IN_PROGRESS = 1
    ENDED = 2
    IN_PREPARATION = 3


class Games(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_1 = db.Column(db.Integer)
    player_2 = db.Column(db.Integer)
    points = db.Column(db.Integer)
    result = db.Column(db.Integer) #kto wygral
    status = db.Column(db.Integer) #1-w trakcie, 2-skonczona


db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)


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


@app.route('/rooms')
@login_required
def play():
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    return render_template('play.html', name=current_user.name, alphabet=alphabet)


@app.route('/rooms', methods=["POST"])
@login_required
def new_game_init():
    if request.method == "POST":
        result = request.get_json()
        enemy = Users.query.filter_by(name=result.get('enemy')).first()
        sql_insert_one = text(
            f"INSERT INTO games(player_1, player_2, points, status, result) \
            VALUES ('{current_user.id}', '{enemy.id}', '{0}', '{1}', '0');")
        db.session.execute(sql_insert_one)
        db.session.commit()
        response_object = {'status': 'success'}
    return response_object


@app.route('/rooms', methods=["PUT"])
@login_required
def end_game():
    if request.method == "PUT":
        result = request.get_json()
        player = result.get('playerNum')
        points = result.get('points')
        sql_insert_one = text(
            f"UPDATE games SET result={player}, status=2, points={points} WHERE status=1 AND player_{player}='{current_user.id}';")
        print(sql_insert_one)
        db.session.execute(sql_insert_one)

        db.session.commit()
        response_object = {'status': 'success'}
    return response_object


@app.route("/pusher/auth", methods=['POST'])
def pusher_authentication():
    auth = pusher.authenticate(
        channel=request.form['channel_name'],
        socket_id=request.form['socket_id'],
        custom_data={
            u'user_id': current_user.name,
            u'user_info': {
                u'role': u'player'
            }
        }
    )
    return json.dumps(auth)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


def get_games_won_for_player_number(player_id):
    return len(Games.query.filter_by(player_1=player_id, result=1).all()) + len(
        Games.query.filter_by(player_2=player_id, result=2).all())

def last_game_with(player_id):
    other_player= Games.query.filter_by(player_1=player_id).order_by(Games.id.desc()).limit(1).all()[0]
    other_player_id=other_player.player_2
    return Users.query.get(other_player_id)

def last_game_numbers(player_id):

    last_orders = db.session.query(
    Games.player_2, db.func.count(Games.player_2).label('mycount')).filter_by(player_1=player_id).group_by(Games.player_2).order_by('mycount').limit(1).all()[0] #.subquery()

    return Users.query.get(last_orders.player_2)

def get_games_won_for_players():
    arr=[]
    arr1=[]
    arr2=[]
    counter=Users.query.order_by(Users.name.asc()).all()
    for elem in counter:
        arr2.append(elem.name)

    for elem in counter:
        arr1.append( len(Games.query.filter_by(player_1=elem.id, result=1).all()) + len(
            Games.query.filter_by(player_2=elem.id, result=2).all()))
    dictionary = dict(zip(arr2, arr1))
    arr.append(dictionary)
    return arr



def get_games_lost_for_player_number(player_id):
    return len(Games.query.filter_by(player_1=player_id, result=2).all()) + len(
        Games.query.filter_by(player_2=player_id, result=1).all())


def get_games_in_progress_for_player_number(player_id):
    return len(Games.query.filter_by(player_1=player_id, result=0).all()) + len(
        Games.query.filter_by(player_2=player_id, result=0).all())

def get_all_available_users():
    users=Users.query.filter_by(status="available").all()
    users_arr=[]
    for user in users:
        users_arr.append(user.name)
    return users_arr

def get_current_user(current_user):
    return current_user.name

def get_all__users():
    users_query=Users.query.all()
    return users_query

def get_all_users_emails():
    users_query=Users.query.all()
    users_arr=[]
    for user in users_query:
        users_arr.append(user.email)
    return users_arr

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                           games_in_progress=get_games_in_progress_for_player_number(current_user.id),
                           games_won=get_games_won_for_player_number(current_user.id),
                           games_lost=get_games_lost_for_player_number(current_user.id),
                           all_available_users=get_all_available_users(),
                           all_users=get_all__users(),
                           all_users_emails=get_all_users_emails(),
                           get_curent_user=get_current_user(current_user),
                           games_won_for_all_players=get_games_won_for_players(),
                           last_game_with=last_game_with(current_user.id),
                           last_game_numbers=last_game_numbers(current_user.id)
                           )


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
            flash('Użytkownik o takim adresie mail już istnieje!')
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


if __name__ == "__main__":
    app.debug = True
    app.run()

name = ''
