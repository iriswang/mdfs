#!/usr/bin/env python

import logging
import requests

from collections import defaultdict
from errno import ENOENT, ENOTEMPTY
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from argparse import ArgumentParser
from base64 import b64decode, b64encode
SERVER = "http://10.5.0.106:5000"

logging.basicConfig(level=logging.DEBUG)

if not hasattr(__builtins__, 'bytes'):
    bytes = str

class MDFS(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self, cookies):
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.cookies=cookies

    def chmod(self, path, mode):
        print "CHMOD", path
        self.files[path]['st_mode'] &= 0770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        print "CHOWN", path
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def create(self, path, mode):
        print "CREATE", path, mode
        response = requests.get(SERVER+"/create", params={
            "path": path
        }, cookies=self.cookies)
        return response.json()['data']['inode']['id']

    def getattr(self, path, fh=None):
        print "GETATTR", path
        response = requests.get(SERVER+"/getattr", params={
            "path": path
        }, cookies=self.cookies)
        print response.text
        json = response.json()
        if json['data'] is None:
            raise FuseOSError(ENOENT)
        else:
            if json['data']['inode']['is_dir']:
                stat = S_IFDIR
            else:
                stat = S_IFREG
            now = time()
            return dict(st_mode=(stat | 0777), st_nlink=1,
                                st_size=json['data']['inode']['size'], st_ctime=time(), st_mtime=time(),
                                st_atime=time())



    def getxattr(self, path, name, position=0):
        print "GETXATTR", path, name
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        print "LISTXATTR", path
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        print "MKDIR", path
        requests.get(SERVER+"/mkdir", params={
            "path": path
        }, cookies=self.cookies)

    def open(self, path, flags):
        print "OPEN", path
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        print "READ", path, size, offset
        response = requests.get(SERVER+"/read", params={
            "path": path,
            "size": size,
            "offset": offset
        }, cookies=self.cookies)
        return str(b64decode(response.json()['data']['data']))

    def readdir(self, path, fh):
        print "READDIR", path
        response = requests.get(SERVER+"/readdir", params={
            "path": path
        }, cookies=self.cookies)
        print response.text
        print response.json()
        files = [x.encode('ascii', 'ignore').replace('/','') for x in response.json()['data']['files']]
        return ['.', '..'] + files

    def readlink(self, path):
        print "READLINE", path
        return self.data[path]

    def removexattr(self, path, name):
        print "REMOVEXATTR", path, name
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        print "RENAME", old, new
        self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        print "RMDIR", path
        response = requests.get(SERVER+"/rmdir", params={
            "path": path
        }, cookies=self.cookies)
        print response.json()
        if response.json()['success'] is False:
            raise FuseOSError(ENOTEMPTY)

    def setxattr(self, path, name, value, options, position=0):
        print "SETXATTR"
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        print "STATFS", path
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        print "SYMLINK"
        self.files[target] = dict(st_mode=(S_IFLNK | 0777), st_nlink=1,
                                  st_size=len(source))

        self.data[target] = source

    def truncate(self, path, length, fh=None):
        print "TRUNCATE", path
        return
        self.data[path] = self.data[path][:length]
        self.files[path]['st_size'] = length

    def unlink(self, path):
        print "UNLINK", path
        response = requests.get(SERVER+"/unlink", params={
            "path": path
        }, cookies=self.cookies)

    def utimens(self, path, times=None):
        return
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        print "WRITE", path, data, offset
        response = requests.get(SERVER+"/write", params={
            "path": path,
            "data": b64encode(data),
            "offset": offset
        }, cookies=self.cookies)
        print response.text
        return response.json()['data']['data_written']


if __name__ == '__main__':
    argparser = ArgumentParser()

    argparser.add_argument('username')
    argparser.add_argument('password')
    argparser.add_argument('mountpoint')

    args = argparser.parse_args()

    logging.getLogger().setLevel(logging.DEBUG)
    response = requests.post(SERVER+"/login", data={
        'username': args.username,
        'password': args.password
    })
    mem = MDFS(response.cookies)
    fuse = FUSE(mem, args.mountpoint, foreground=True)
