"""
MDFS
"""
from flask import render_template
from flask import make_response
from flask import Flask, request, jsonify
from auth import Authenticator
from functools import wraps
from fs import FileSystem

import requests
from urlparse import urlparse
from werkzeug import url_decode
from base64 import b64encode, b64decode

app = Flask(__name__, static_url_path='')

# Arg parameters
TOKEN = "token"
INODE = "inode"
SERVICE_TOKEN = "access_token"
SERVICE = "service"
PATH = "path"
OLD_PATH = "old_path"
NEW_PATH = "new_path"

# JSON response keys
JSON_SUCCESS = "success"
JSON_DATA = "data"
JSON_ERROR = "error"
ERROR_MESSAGE = "Error message: {message}"

# User parameters
USERNAME = "username"
PASSWORD = "password"

FB_CLIENT_ID = "1570250713202324"
FB_CLIENT_SECRET = "25fdcad49fc80d5fa7da9be620d9d122"

app.authenticator = Authenticator()
app.fs = FileSystem()

def requires_authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get(TOKEN)
        if token:
            if app.authenticator.check_token(token):
                return f(*args, **kwargs)
        return render_template('/login.html')
    return decorated

@app.route('/login', methods=['GET'])
def render_login():

    # if token is invalid, redirect user to login page
    token = request.cookies.get(TOKEN)
    if not app.authenticator.check_token(token):
        return render_template('/login.html')
    else:
        return index()

@app.route("/")
@requires_authentication
def index():
    return render_template('/index.html')

@app.route("/callback")
def soundcloud_callback():
    return render_template('/callback.html')

@app.route('/login', methods=['POST'])
def login_user():
    req_dict = request.form
    if USERNAME in req_dict and PASSWORD in req_dict:
        username = req_dict[USERNAME]
        password = req_dict[PASSWORD]

        # if the user already exists, log him/her in
        if app.authenticator.is_user(username):
            if app.authenticator.check_password(username, password):
                pass
            else:
                raise Exception
        # the user does not exist, create one
        else:
            app.authenticator.add_user(username, password)

        new_token = app.authenticator.gen_token(username)
        resp = make_response(render_template('/index.html'))
        resp.set_cookie(TOKEN, new_token.encode('utf8'))
        return resp
    return render_login()

# @app.route('/user', methods=['DELETE'])
# @requires_authentication
# def delete_user():
#     req_args = request.args
#     if USERNAME in req_args.keys():
#         username = req_args[USERNAME]
#         try:
#             app.authenticator.delete_user(username)
#             return jsonify({JSON_SUCCESS: True, JSON_DATA: None,
#                             JSON_ERROR: None})
#         except Exception as e:
#             return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
#                             JSON_ERROR: ERROR_MESSAGE.format(message=e.message)})
#     return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
#                         JSON_ERROR: ERROR_MESSAGE.format(field="username or password")})

@app.route('/initialize', methods=['POST'])
@requires_authentication
def add_service_token():
    print "ADD SERVICE TOKEN"
    req_json = request.form
    token = get_token_from_cookie(request)
    if SERVICE in req_json and SERVICE_TOKEN in req_json:
        access_token = req_json[SERVICE_TOKEN]
        # TODO (Yuxin) assumes it never expires...
        if req_json[SERVICE] == 'facebook':
            access_token = get_extended_fb_token(req_json[SERVICE_TOKEN])
        try:
            app.authenticator.add_service_token(token, req_json[SERVICE],
                                                access_token)
            return jsonify({JSON_SUCCESS: True, JSON_DATA: None,
                            JSON_ERROR: None})
        except Exception as e:
            print e
            return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                            JSON_ERROR: ERROR_MESSAGE.
                            format(message=e.message)})
    else:
        return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                        JSON_ERROR: ERROR_MESSAGE.
                        format(message="missing service field")})

def get_token_from_cookie(request):
    return request.cookies.get(TOKEN)

def get_extended_fb_token(access_token):
    # print access_token
    payload = {'client_id': FB_CLIENT_ID, 'client_secret': FB_CLIENT_SECRET, 'grant_type': 'fb_exchange_token', 'fb_exchange_token': access_token}
    r = requests.get("https://graph.facebook.com/oauth/access_token", params=payload)
    try:
        access_token = url_decode(r.text).get('access_token')
    except Exception as e:
        print '(WARNING) Failed to parse retrieve long-lived access token', r.text
    print 'EXPIRES: ' + url_decode(r.text).get('expires')
    return access_token

########## FS API CALLS ###########
def check_path(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        req_args = request.args
        if PATH in req_args.keys():
            try:
                data = f(*args, **kwargs)
                return jsonify({JSON_SUCCESS: True, JSON_DATA: data,
                                JSON_ERROR: None})
            except Exception as e:
                return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                                JSON_ERROR: ERROR_MESSAGE.
                                format(message=e.message)})
        else:
            return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                            JSON_ERROR: ERROR_MESSAGE.
                            format(message="missing path field")})
    return decorated

@app.route("/create", methods=['GET'])
@check_path
def create():
    path = request.args[PATH]
    inode = app.fs.create(path, None)
    return {"inode": {
        'id': inode.id,
        'is_dir': inode.is_dir
    }}

@app.route("/mkdir", methods=['GET'])
@check_path
def mkdir():
    path = request.args[PATH]
    app.fs.mkdir(path, None)


@app.route("/readdir", methods=['GET'])
@check_path
def readdir():
    path = request.args[PATH]
    files = app.fs.readdir(path, None)
    return {"files": files}

@app.route("/getattr", methods=['GET'])
@check_path
def getattr():
    path = request.args[PATH]
    inode = app.fs.getattr(path, None)
    return {"inode": {
        'id': inode.id,
        'is_dir': inode.is_dir
    }}


@app.route("/rmdir", methods=['GET'])
@check_path
def rmdir():
    path = request.args[PATH]
    app.fs.rmdir(path, None)


@app.route("/unlink", methods=['GET'])
@check_path
def unlink():
    path = request.args[PATH]
    app.fs.unlink(path, None)

@app.route("/read", methods=['GET'])
@check_path
def read():
    path = request.args[PATH]
    size = int(request.args['size'])
    offset = int(request.args['offset'])
    return {
        "data": b64encode(app.fs.read(path, size, offset, None, None))
    }

@app.route("/write", methods=['GET'])
@check_path
def write():
    path = request.args[PATH]
    data = b64decode(request.args['data'])
    offset = int(request.args['offset'])
    return {
        "data": b64encode(app.fs.write(path, data, offset, None, None))
    }

@app.route("/rename", methods=['GET'])
def rename():
    req_args = request.args
    if NEW_PATH in req_args.keys() and OLD_PATH in req_args.keys():
        old_path = req_args[OLD_PATH]
        new_path = req_args[NEW_PATH]
        try:
            app.fs.rename(old_path, new_path)
            return jsonify({JSON_SUCCESS: True, JSON_DATA: None,
                            JSON_ERROR: None})
        except Exception as e:
            return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                            JSON_ERROR: ERROR_MESSAGE.
                            format(message=e.message)})
    else:
        return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                        JSON_ERROR: ERROR_MESSAGE.
                        format(message="missing old_path and new_path field")})

if __name__ == '__main__':
    app.run(debug=True)
