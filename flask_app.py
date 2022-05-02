import os

import psycopg2
from flask import Flask, request, redirect, render_template
from urllib.parse import urlparse, urlunparse

app = Flask(__name__)


# FROM_DOMAIN = "statki.pythonanywhere.com"
# TO_DOMAIN = "149.156.43.57/p23"

def get_db_connection():
    conn = psycopg2.connect(host='ec2-52-212-228-71.eu-west-1.compute.amazonaws.com',
                            database='db1955gb2mvu3g',
                            user='jslsutrxhbtyxw',
                            password='4547e639209c8471045b50057d23b3f7f8911b88bcfd001fd87b7785ef3f543e')
    # user = os.environ['DB_USERNAME'],
    # password = os.environ['DB_PASSWORD'])
    return conn


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/rooms')
def hello_world_rooms():
    return render_template('rooms.html',
                           users=get_gamers(),
                           available=get_gamers('available'),
                           in_game=get_gamers('in_game'))


def get_gamers(status=None):
    connected_db = get_db_connection()
    cur = connected_db.cursor()
    formula = f'WHERE status=\'{status}\'' if status else ''
    cur.execute(f'SELECT * FROM users {formula}')
    gamers = cur.fetchall()
    cur.close()
    connected_db.close()
    return gamers


# @app.before_request
# def redirect_to_new_domain():
#     urlparts = urlparse(request.url)
#     if urlparts.netloc == FROM_DOMAIN:
#         urlparts_list = list(urlparts)
#         urlparts_list[1] = TO_DOMAIN
#     return redirect(urlunparse(urlparts_list), code=301)

if __name__ == '__main__':
    app.run(debug=False)
