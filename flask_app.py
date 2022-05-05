import psycopg2
from flask import Flask,  request, redirect, render_template, session
from urllib.parse import urlparse, urlunparse
import bcrypt
from flask import *

SESSION_TYPE = 'memcache'

app = Flask(__name__)
app.secret_key = 'super secret key'


def get_db_connection():
    conn = psycopg2.connect(host='ec2-34-242-8-97.eu-west-1.compute.amazonaws.com',
                            database='d9qk23pnab16ud',
                            user='qbhjnrrwqvchoi',
                            password='a12038c8f5d69267b00001db8cd0762c79458d0ec0cf8399467df7e04d1d8d50')
    # user = os.environ['DB_USERNAME'],
    # password = os.environ['DB_PASSWORD'])
    return conn


def get_gamers(status=None):
    connected_db = get_db_connection()
    cur = connected_db.cursor()
    formula = f'WHERE status=\'{status}\'' if status else ''
    cur.execute(f'SELECT * FROM users {formula}')
    gamers = cur.fetchall()
    cur.close()
    connected_db.close()
    return gamers

# FROM_DOMAIN = "statki.pythonanywhere.com"
# TO_DOMAIN = "149.156.43.57/p23"

# render głównej strony


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    # jeśli nie połączy się z bazą to rzucaj błąd -dodać
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    remember = True if request.form.get(
        'remember') else False  # zapamietaj mnie
    connected_db = get_db_connection()
    cur = connected_db.cursor()
    cur.execute("SELECT * FROM users WHERE name =%s", [username])
    if cur is not None:
        data = cur.fetchone()  # zwraca pojedynczą krotkę
        try:
            password = data[2]  # kolumna password
        except Exception:
            print("jestem tu4")
            error = 'Nieprawidłowy Login lub hasło'
            # flash('Nieprawidłowy Login lub hasło') # wyświetlać tutaj info na temat że nieprawdiłowe hasło
            return redirect(url_for('login'))
        # if bcrypt.checkpw(password.encode('utf-8'), data[2].encode('utf-8')): dodać bcrypt
        print()
        if password == data[2]:
            app.logger.info('Password Matched')
            # session['logged_in'] = True
            # session['username'] = username
            # flash('You are now logged in', 'success') # dodać wyświetlanie tego
            cur.close()
            return redirect(url_for('show_rooms'))
        else:
            error = 'Nieprawidłowy Login lub hasło'
            return render_template('login.html', error=error)
    else:
        error = 'Nieprawidłowy Login lub hasło'
        return render_template('login.html', error=error)


@app.route('/forget')
def forget_password():
    return render_template('forget_password.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/logout')
def logout():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/rooms')
def show_rooms():
    return render_template('rooms.html',
                           users=get_gamers(),
                           available=get_gamers('available'),
                           in_game=get_gamers('in_game'))


@app.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('password')
    # email = StringField(label='E-mail', validators=[
    #     validators.Length(min=5, max=35), validators.Email()
    # ])
    # password = StringField(label='Password', validators=[
    #     validators.Length(min=6, max=10),
    #     validators.EqualTo('password_confirm', message='Passwords must match')
    # ])
    # password_confirm = StringField(label='Password confirm', validators=[
    #     validators.Length(min=6, max=10)
    # ])
    print(email, name, password)
    return email, name, password

# @app.before_request
# def redirect_to_new_domain():
#     urlparts = urlparse(request.url)
#     if urlparts.netloc == FROM_DOMAIN:
#         urlparts_list = list(urlparts)
#         urlparts_list[1] = TO_DOMAIN
#     return redirect(urlunparse(urlparts_list), code=301)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)
    app.run(debug=True)
