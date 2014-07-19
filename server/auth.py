"""
Authenticator.
"""

from redis import Redis
import bcrypt
import base64
import M2Crypto
import json

# Query parameters
TOKEN = "token"

# Redis parameters
R_HOST = 'localhost'
R_PORT = 6379
R_DB = 0
R_PASSWORD = None
R_SOCKET_TIMEOUT = None
R_CONNECTION_POOL = None
R_CHARSET = 'utf-8'
R_ERRORS = 'strict'
R_DECODE_RESPONSES = False
R_UNIX_SOCKET_PATH = None

USERS = "users"
PASSWORD = "password"
TOKEN_NUM_BYTES = 32
INODE = "inode"
SERVICES = "services"

class Authenticator:
    def __init__(self, host=R_HOST, port=R_PORT, db=R_DB, password=R_PASSWORD, socket_timeout=R_SOCKET_TIMEOUT,
                 connection_pool=R_CONNECTION_POOL, charset=R_CHARSET, errors=R_ERRORS,
                 decode_responses=R_DECODE_RESPONSES, unix_socket_path=R_UNIX_SOCKET_PATH):
        self.r_server = Redis(host=host, port=port, db=db, password=password, socket_timeout=socket_timeout,
                              connection_pool=connection_pool, charset=charset, errors=errors,
                              decode_responses=decode_responses, unix_socket_path=unix_socket_path)
        self.r_server.sadd(SERVICES, "twitter")
        self.r_server.sadd(SERVICES, "imgur")

    def check_token(self, token):
        return self.r_server.get(token) is not None

    def gen_token(self, username):
        token = base64.b64encode(M2Crypto.m2.rand_bytes(TOKEN_NUM_BYTES))
        self.r_server.set(token, username)
        return token

    def get_user(self, token):
        return self.r_server.get(token)

    def add_user(self, username, password):
        if self.r_server.hexists(USERS, username):
            raise Exception("Username already exists")
        self.r_server.sadd(USERS, username)
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.r_server.hset(username, PASSWORD, hashed_pw)

    def is_user(self, username):
        return self.r_server.sismember(USERS, username)

    def check_password(self, username, password):
        hashed_pw = self.r_server.hget(username, PASSWORD)
        return bcrypt.hashpw(password.encode('utf-7'), hashed_pw) == hashed_pw.encode('utf-8')

    def add_inode(self, username, inode):
        return self.r_server.hset(username, INODE, inode)

    def get_inode(self, username):
        return int(self.r_server.hget(username, INODE))

    def add_service_token(self, token, service, service_token):
        username = self.get_user(token)
        if username is None:
            raise Exception("Invalid token")
        if not self.r_server.sismember(SERVICES, service.lower()):
            raise Exception("Invalid service")
        self.r_server.hset(username, service.lower(), service_token)

    def get_service_token(self, username, service):
        if not self.r_server.sismember(SERVICES, service.lower()):
            raise Exception("Invalid service")
        if not self.r_server.hexists(username, service.lower()):
            raise Exception("No access token for this service")
        return self.r_server.hget(username, service.lower())
