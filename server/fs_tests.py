import nose
from nose.tools import eq_, ok_, raises
from fs import FileSystem
from models import Base
import requests

BASE_URL = "http://127.0.0.1:5000/"
DATA = "data"
FILES = "files"

class TestFS:

    fs = FileSystem()

    @classmethod
    def setup_class(cls):
        Base.metadata.create_all(cls.fs.engine)

    @classmethod
    def teardown_class(cls):
        Base.metadata.drop_all(cls.fs.engine)

    setup = setup_class
    teardown = teardown_class

    def test_mkdir(self):
        self.fs.mkdir("/folder1")
        eq_(self.fs.readdir("/"), ["folder1/"])
        self.fs.mkdir("/folder2")
        eq_(self.fs.readdir("/"), ["folder1/", "folder2/"])
        self.fs.rmdir("/folder2")
        eq_(self.fs.readdir("/"), ["folder1/"])
        self.fs.rename("/folder1", "/folder2")
        eq_(self.fs.readdir("/"), ["folder2/"])

    def test_mkdir_nested(self):
        self.fs.mkdir("/folder1")
        eq_(self.fs.readdir("/"), ["folder1/"])
        self.fs.mkdir("/folder1/nested_folder")
        eq_(self.fs.readdir("/"), ["folder1/"])
        eq_(self.fs.readdir("/folder1"), ["nested_folder/"])
        self.fs.create("/folder1/nested_folder/file1")
        eq_(self.fs.readdir("/"), ["folder1/"])
        eq_(self.fs.readdir("/folder1"), ["nested_folder/"])
        eq_(self.fs.readdir("/folder1/nested_folder"), ["file1"])
        self.fs.create("/folder1/nested_folder/file2")
        eq_(self.fs.readdir("/"), ["folder1/"])
        eq_(self.fs.readdir("/folder1"), ["nested_folder/"])
        eq_(self.fs.readdir("/folder1/nested_folder"), ["file1", "file2"])
        self.fs.unlink("/folder1/nested_folder/file1")
        eq_(self.fs.readdir("/folder1/nested_folder"), ["file2"])
        self.fs.rename("/folder1/nested_folder/file2", "/folder1/file1")
        eq_(self.fs.readdir("/folder1/nested_folder"), [])
        eq_(self.fs.readdir("/folder1"), ["file1", "nested_folder/"])

    def test_mkdir_requests(self):
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
    r = requests.get(BASE_URL + method, params=payload)
    response = r.json()
    return response

def rename_request(old_path, new_path):
    payload = {"old_path": old_path, "new_path": new_path}
    r = requests.get(BASE_URL + "rename", params=payload)
    response = r.json()
    return response

if __name__ == "__main__":
    nose.run()
