from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,\
    Boolean, UniqueConstraint

Base = declarative_base()

class INode(Base):
    __tablename__ = "inode"
    id = Column("id", Integer, primary_key=True)
    is_dir = Column("is_dir", Boolean, default=False)
    name = Column("name", String(255))
    parent_inode = Column("parent_inode", Integer, ForeignKey("inode.id"))
    UniqueConstraint("name", "parent_inode")

    def __repr__(self):
        return "<INode(name='%s', parent_inode='%s')" % (self.name, str(self.parent_inode))
