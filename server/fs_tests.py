import nose
from nose.tools import eq_, ok_, raises
from fs import FileSystem
from models import Base


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

if __name__ == "__main__":
    nose.run()
