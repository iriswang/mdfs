from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,\
    Boolean

Base = declarative_base()

class INode(Base):
    __tablename__ = "inode"
    id = Column("id", Integer, primary_key=True)
    is_dir = Column("is_dir", Boolean, default=False)
    parent_inode = Column("parent_inode", Integer, ForeignKey("inode.id"))

