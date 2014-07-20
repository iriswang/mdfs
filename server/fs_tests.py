import nose
from nose.tools import eq_, ok_, raises
from fs import FileSystem
from models import Base
import requests
from redis import Redis

BASE_URL = "http://127.0.0.1:5000/"
DATA = "data"
FILES = "files"

class TestFS:

    fs = FileSystem()
    r_server = Redis()

    @classmethod
    def setup_class(cls):
        Base.metadata.create_all(cls.fs.engine)

    @classmethod
    def teardown_class(cls):
        Base.metadata.drop_all(cls.fs.engine)
        cls.r_server.flushdb()

    setup = setup_class
    teardown = teardown_class


    def test_mkdir(self):
        inode = self.fs.create_user_inode()
        self.fs.mkdir("/folder1", inode)
        eq_(self.fs.readdir("/", inode), ["folder1/"])
        self.fs.mkdir("/folder2", inode)
        eq_(self.fs.readdir("/", inode), ["folder1/", "folder2/"])
        self.fs.rmdir("/folder2", inode)
        eq_(self.fs.readdir("/", inode), ["folder1/"])
        self.fs.rename("/folder1", "/folder2", inode)
        eq_(self.fs.readdir("/", inode), ["folder2/"])

    def test_mkdir_nested(self):
        inode = self.fs.create_user_inode()
        self.fs.mkdir("/folder1", inode)
        eq_(self.fs.readdir("/", inode), ["folder1/"])
        self.fs.mkdir("/folder1/nested_folder", inode)
        eq_(self.fs.readdir("/", inode), ["folder1/"])
        eq_(self.fs.readdir("/folder1", inode), ["nested_folder/"])
        self.fs.create("/folder1/nested_folder/file1", inode)
        eq_(self.fs.readdir("/", inode), ["folder1/"])
        eq_(self.fs.readdir("/folder1", inode), ["nested_folder/"])
        eq_(self.fs.readdir("/folder1/nested_folder", inode), ["file1"])
        self.fs.create("/folder1/nested_folder/file2", inode)
        eq_(self.fs.readdir("/", inode), ["folder1/"])
        eq_(self.fs.readdir("/folder1", inode), ["nested_folder/"])
        eq_(self.fs.readdir("/folder1/nested_folder", inode), ["file1", "file2"])
        self.fs.unlink("/folder1/nested_folder/file1", inode)
        eq_(self.fs.readdir("/folder1/nested_folder", inode), ["file2"])
        self.fs.rename("/folder1/nested_folder/file2", "/folder1/file1", inode)
        eq_(self.fs.readdir("/folder1/nested_folder", inode), [])
        eq_(self.fs.readdir("/folder1", inode), ["file1", "nested_folder/"])

    def test_mkdir_requests(self):
        global IRIS_TOKEN
        IRIS_TOKEN = login("iris", "password")
        get_request("mkdir", "/folder1")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder1/"])
        get_request("mkdir", "/folder2")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder1/", "folder2/"])
        get_request("rmdir", "/folder2")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder1/"])
        rename_request("/folder1", "/folder2")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder2/"])
        get_request("rmdir", "/folder2")

    def test_mkdir_nested_requests(self):
        global IRIS_TOKEN
        IRIS_TOKEN = login("iris", "password")
        get_request("mkdir","/folder1")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder1/"])
        get_request("mkdir", "/folder1/nested_folder")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder1/"])
        eq_(get_request("readdir", "/folder1")[DATA][FILES], ["nested_folder/"])
        get_request("create", "/folder1/nested_folder/file1")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder1/"])
        eq_(get_request("readdir", "/folder1")[DATA][FILES], ["nested_folder/"])
        eq_(get_request("readdir", "/folder1/nested_folder")[DATA][FILES], ["file1"])
        get_request("create", "/folder1/nested_folder/file2")
        eq_(get_request("readdir", "/")[DATA][FILES], ["folder1/"])
        eq_(get_request("readdir", "/folder1")[DATA][FILES], ["nested_folder/"])
        eq_(get_request("readdir", "/folder1/nested_folder")[DATA][FILES], ["file1", "file2"])
        get_request("unlink", "/folder1/nested_folder/file1")
        eq_(get_request("readdir", "/folder1/nested_folder")[DATA][FILES], ["file2"])
        rename_request("/folder1/nested_folder/file2", "/folder1/file1")
        eq_(get_request("readdir", "/folder1/nested_folder")[DATA][FILES], [])
        eq_(get_request("readdir", "/folder1")[DATA][FILES], ["file1", "nested_folder/"])
        get_request("rmdir", "/folder1/nested_folder")
        get_request("unlink", "/folder1/file1")
        get_request("rmdir", "/folder1")

def get_request(method, path):
    payload = {"path": path}
    cookies = dict(token=IRIS_TOKEN)
    r = requests.get(BASE_URL + method, params=payload, cookies=cookies)
    response = r.json()
    return response

def rename_request(old_path, new_path):
    payload = {"old_path": old_path, "new_path": new_path}
    cookies = dict(token=IRIS_TOKEN)
    r = requests.get(BASE_URL + "rename", params=payload, cookies=cookies)
    print "R.TEXT: ", r.text
    response = r.json()
    return response

def login(username, password):
    payload = {'username': username, 'password': password}
    r = requests.post(BASE_URL + "login", data=payload)
    return r.cookies["token"]

IRIS_TOKEN = login("iris", "password")
print "IRIS_TOKEN: ", IRIS_TOKEN
if __name__ == "__main__":
    nose.run()
