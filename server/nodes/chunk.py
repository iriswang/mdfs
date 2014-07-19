from multiprocessing import Rlock

lock = Rlock()

class Chunk:

    def __init__(self, data, size, index, offset):
        self.data = data
        self.size = size
        self.index = index
        self.offset = offset
        self.info = {}

    def update_info(self, service, info):
        with lock:
            self.info[service] = info
