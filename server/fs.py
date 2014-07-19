from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, INode
import os

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'inode.db')

class FileSystem:

    def __init__(self):
        self.engine = create_engine(DATABASE_URI)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create(self, path, mode):
        pass

    def getattr(self, path, fh=None):
        pass

    def mkdir(self, path, mode):
        pass

    def open(self, path, flags):
        pass

    def read(self, path, size, offset, fh):
        pass

    def readdir(self, path, fh):
        pass

    def rename(self, old, new):
        pass

    def rmdir(self, path):
        pass

    def write(self, path, data, offset, fh):
        pass

    def get_inode(self, path):
        pass
