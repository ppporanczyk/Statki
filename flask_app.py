
from flask import Flask,  request, redirect, render_template
from urllib.parse import urlparse, urlunparse


app = Flask(__name__)


# FROM_DOMAIN = "statki.pythonanywhere.com"
# TO_DOMAIN = "149.156.43.57/p23"


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/rooms')
def hello_world_rooms():
    x = ''
    str = ''
    return 'We have no rooms yet'


# @app.before_request
# def redirect_to_new_domain():
#     urlparts = urlparse(request.url)
#     if urlparts.netloc == FROM_DOMAIN:
#         urlparts_list = list(urlparts)
#         urlparts_list[1] = TO_DOMAIN
#     return redirect(urlunparse(urlparts_list), code=301)
