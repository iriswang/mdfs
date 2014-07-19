"""
MDFS
"""
from flask import render_template
from flask import Flask, request, jsonify
from auth import Authenticator
from functools import wraps
app = Flask(__name__, static_url_path='')

# Arg parameters
TOKEN = "token"
INODE = "inode"
SERVICE_TOKEN = "access_token"
SERVICE = "service"

# JSON response keys
JSON_SUCCESS = "success"
JSON_DATA = "data"
JSON_ERROR = "error"
ERROR_MESSAGE = "Error message: {error}"

# User parameters
USERNAME = "username"
PASSWORD = "password"

app.authenticator = Authenticator()


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/callback")
def soundcloud_callback():
    return render_template('/callback.html')

def requires_authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        req_args = request.args
        if TOKEN in req_args.keys():
            if app.authenticator.check_token(req_args[TOKEN]):
                return f(*args, **kwargs)
        return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                        JSON_ERROR: ERROR_MESSAGE.
                        format(error="Not authenticated")})
    return decorated


# @app.route('/login', methods=['GET'])
# def authenticate_request():
#     req_args = request.args
#     if USERNAME in req_args.keys() and PASSWORD in req_args.keys():
#         username = req_args[USERNAME]
#         password = req_args[PASSWORD]
#         if app.authenticator.check_password(username, password):
#             new_token = app.authenticator.gen_token(username)
#             return jsonify({JSON_SUCCESS: True, JSON_DATA:
#                             {TOKEN: new_token.encode('utf8')},
#                             JSON_ERROR: None})
#     return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
#                     JSON_ERROR: ERROR_MESSAGE.
#                     format(error="invalid username or password/ missing fields")})


@app.route('/login', methods=['GET'])
def render_login():
    return render_template('/login.html')

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
        print resp
        return resp
    render_login()

    # req_json = request.get_json()

    #     try:
    #         app.authenticator.add_user(username, password)
    #     except Exception as e:
    #         return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
    #                         JSON_ERROR: ERROR_MESSAGE.
    #                         format(field=e.message)})
    #     return jsonify({JSON_SUCCESS: True, JSON_DATA: None,
    #                     JSON_ERROR: None})
    # else:
    #     return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
    #                     JSON_ERROR: ERROR_MESSAGE.
    #                     format(message="missing username or password fields")})
    #     resp = make_response(render_template('/index.html'))
    #     resp.set_cookie()
    #     return resp

@app.route('/user', methods=['DELETE'])
@requires_authentication
def delete_user():
    req_args = request.args
    if USERNAME in req_args.keys():
        username = req_args[USERNAME]
        try:
            app.authenticator.delete_user(username)
            return jsonify({JSON_SUCCESS: True, JSON_DATA: None,
                            JSON_ERROR: None})
        except Exception as e:
            return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                            JSON_ERROR: ERROR_MESSAGE.format(message=e.message)})
    return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                        JSON_ERROR: ERROR_MESSAGE.format(field="username or password")})


@app.route('/initialize', methods=['POST'])
@requires_authentication
def add_service_token():
    req_json = request.get_json()
    print req_json
    req_args = request.args
    if SERVICE in req_json.keys() and SERVICE_TOKEN in req_json.keys():
        try:
            print req_args[TOKEN]
            app.authenticator.add_service_token(req_args[TOKEN], req_json[SERVICE],
                                                req_json[SERVICE_TOKEN])
            return jsonify({JSON_SUCCESS: True, JSON_DATA: None,
                            JSON_ERROR: None})
        except Exception as e:
            return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                            JSON_ERROR: ERROR_MESSAGE.
                            format(message=e.message)})
    else:
        return jsonify({JSON_SUCCESS: False, JSON_DATA: None,
                        JSON_ERROR: ERROR_MESSAGE.
                        format(message="missing service field")})


if __name__ == '__main__':
    app.run(debug=True)
