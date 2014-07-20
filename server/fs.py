from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, INode
from redis import Redis
from chunker import CHUNK_SIZE, get_chunks, allocate_chunks_to_service
from nodes import Chunk
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'inode.db')
DB_NUM = 1


class FileSystem:

    def __init__(self):
        self.engine = create_engine(DATABASE_URI)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        self.r_server = Redis(db=DB_NUM)

    def create(self, path, root_inode_id, mode=None):
        session = self.session()
        split_path = os.path.split(path)
        parent_inode = self.get_inode(split_path[0], root_inode_id)
        new_name = split_path[1]
        try:
            if parent_inode.is_dir:
                new_inode = INode(name=new_name, parent_inode=parent_inode.id)
            else:
                raise Exception("Parent is not a directory")
            session.add(new_inode)
            session.commit()
            self.r_server.set("inode_"+str(new_inode.id), json.dumps([]))
            return new_inode
        finally:
            session.close()

    def getattr(self, path, root_inode_id, fh=None):
        inode = self.get_inode(path, root_inode_id)
        chunk_json = json.loads(self.r_server.get("inode_"+str(inode.id)))
        chunk_list = map(Chunk.load, chunk_json)
        file_length = sum([x.size for x in chunk_list])
        return inode, file_length

    def mkdir(self, path, root_inode_id, mode=None):
        session = self.session()
        split_path = os.path.split(path)
        parent_inode = self.get_inode(split_path[0], root_inode_id)
        new_inode = split_path[1]
        try:
            if parent_inode.is_dir:
                new_inode = INode(is_dir=True, name=new_inode, parent_inode=parent_inode.id)
            else:
                raise Exception("parent is not a directory")
            session.add(new_inode)
            session.commit()
        finally:
            session.close()

    def open(self, path, flags, root_inode_id):
        pass

    def read(self, path, size, offset, fh, root_inode_id):
        try:
            inode = self.get_inode(path, root_inode_id)
            chunk_json = json.loads(self.r_server.get("inode_"+str(inode.id)))
            print chunk_json
            print "KEY", "inode_"+str(inode.id)
            if len(chunk_json) == 0:
                return bytearray([])
            chunk_list = map(Chunk.load, chunk_json)
            end_offset = size + offset

            start = offset / CHUNK_SIZE
            end = (end_offset - 1) / CHUNK_SIZE
            chunks_to_fetch = chunk_list[start:end + 1]

            chunk_dump = get_chunks(chunks_to_fetch, {
                "facebook": None,
                "soundcloud": None,
                "imgur": None,
                "dropbox": None
            }, inode.id)
            bytes = bytearray([])
            for chunk in chunk_dump:
                print chunk
                bytes.extend(chunk.data)

            bytes_begin_offset = offset - chunk_list[start].offset
            print "BYTES", str(bytes)
            return bytes[bytes_begin_offset:bytes_begin_offset + size]
        except:
            logging.exception("OH NO")


    def readdir(self, path, root_inode_id, fh=None):
        result = []
        session = self.session()
        folder_path = self.get_inode(path, root_inode_id)
        try:
            if not folder_path.is_dir:
                raise Exception("Not a directory")
            files = session.query(INode).filter_by(parent_inode=folder_path.id)
            for file_obj in files:
                if file_obj.is_dir:
                    result.append(file_obj.name + "/")
                else:
                    result.append(file_obj.name)
            result.sort()
            return result
        finally:
            session.close()

    def rename(self, old, new, root_inode_id):
        session = self.session()
        old_inode = self.get_inode(old, root_inode_id)
        new_split_path = os.path.split(new)
        new_parent_inode = self.get_inode(new_split_path[0], root_inode_id)
        try:
            if new_parent_inode.is_dir:
                old_inode.parent_inode = new_parent_inode.id
            else:
                raise Exception("Parent is not a directory")
            old_inode.name = new_split_path[1]
            session.add(old_inode)
            session.commit()
        finally:
            session.close()

    def rmdir(self, path, root_inode_id):
        session = self.session()
        if len(self.readdir(path, root_inode_id)) != 0:
            raise Exception("Directory not empty.")
        split_path = os.path.split(path)
        parent_inode = self.get_inode(split_path[0], root_inode_id)
        try:
            inode_to_delete = session.query(INode).\
                filter_by(parent_inode=parent_inode.id,
                            name=split_path[1], is_dir=True).one()
            session.delete(inode_to_delete)
            session.commit()
        finally:
            session.close()

    def unlink(self, path, root_inode_id):
        file_to_delete = self.get_inode(path, root_inode_id)
        if file_to_delete.is_dir:
            raise Exception("Cannot delete directory")
        else:
            try:
                session = self.session()
                session.delete(file_to_delete)
                session.commit()
            finally:
                session.close()

    def write(self, path, data, offset, root_inode_id, fh=None):

        try:
            print type(data)
            print "DATA", type(data[0])
            inode = self.get_inode(path, root_inode_id)
            chunk_json = json.loads(self.r_server.get("inode_"+str(inode.id)))
            chunk_list = map(Chunk.load, chunk_json)
            end_offset = len(data) + offset
            data_written = 0
            file_length = sum([x.size for x in chunk_list])
            chunk_index = len(chunk_list)
            chunk_offset = chunk_index * CHUNK_SIZE

            start = offset / CHUNK_SIZE
            end = (end_offset - 1) / CHUNK_SIZE
            print file_length
            print offset
            if (offset > 0 and file_length < offset):
                raise Exception('File length shorter than offset')

            chunks_to_get = []
            if (len(chunk_list) > 0 and len(chunk_list) >= start):
                chunks_to_get.append(chunk_list[start])

            if (start != end):
                chunks_to_get.append(chunk_list[end])

            got_chunks = get_chunks(chunks_to_get, {
                "facebook": None,
                "soundcloud": None,
                "imgur": None,
                "dropbox": None
            }, inode.id)
            for got_chunk in got_chunks:
                chunk_list[got_chunk.index].data = got_chunk.data


            for chunk in chunk_list:

                if (chunk.index == start):
                    size_of_first_chunk = CHUNK_SIZE if end_offset > CHUNK_SIZE else end_offset
                    size_of_original_data = offset - chunk.offset
                    chunk.data = chunk.data[0:size_of_original_data] + data[0:size_of_first_chunk - size_of_original_data]
                    chunk.size = size_of_first_chunk
                    data_written += size_of_first_chunk - size_of_original_data

                if (chunk.index > start and chunk.index < end):
                    chunk.data = data[data_written:data_written + CHUNK_SIZE]
                    data_written += CHUNK_SIZE

                if (start != end and chunk.index == end):
                    size_of_data_written = end_offset - chunk.offset
                    size_of_end_chunk = chunk.size if end_offset < chunk.offset + chunk.size else size_of_data_written
                    chunk.data = data[data_written:data_written + size_of_data_written] + chunk.data[size_of_data_written:size_of_end_chunk]
                    data_written += size_of_data_written

            while(data_written < len(data)):
                new_chunk_data = data[data_written: data_written + CHUNK_SIZE]
                chunk = Chunk(new_chunk_data, len(new_chunk_data), chunk_index, chunk_offset)
                chunk_index += 1
                chunk_offset += CHUNK_SIZE
                data_written += chunk.size
                chunk_list.append(chunk)

            print "CHUNKLIST", chunk_list[start:end+1]
            chunk_dump = chunk_json[0:start] + allocate_chunks_to_service(chunk_list[start:end+1], inode.id) + chunk_json[end+1:]
            print "KEY", "inode_"+str(inode.id), json.dumps(chunk_dump)
            self.r_server.set("inode_"+str(inode.id), json.dumps(chunk_dump))
            print json.loads(self.r_server.get("inode_"+str(inode.id)))
            print data_written
            return data_written
        except:
            logging.exception("OH HO")

    def create_user_inode(self):
        session = self.session()
        try:
            new_inode = INode(parent_inode=None, is_dir=True)
            session.add(new_inode)
            session.commit()
            return new_inode.id
        finally:
            session.close()

    def get_inode(self, path, root_inode_id):
        session = self.session()
        path_parts = split_path(path)
        curr_inode = None
        try:
            for count, part in enumerate(path_parts):
                if count == 0:
                    curr_inode = session.query(INode).filter(INode.id == root_inode_id).one()
                else:
                    curr_inode = session.query(INode).\
                        filter_by(parent_inode=curr_inode.id, name=part).one()
            return curr_inode
        finally:
            session.close()


def split_path(path, maxdepth=20):
    (head, tail) = os.path.split(path)
    return split_path(head, maxdepth - 1) + [tail] \
        if maxdepth and head and head != path \
        else [head or tail]

if __name__ == "__main__":
    fs = FileSystem()
