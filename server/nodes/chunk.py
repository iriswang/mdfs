from multiprocessing import Lock

lock = Lock()

class Chunk:

    def __init__(self, data, size, index, offset):
        self.data = data
        self.size = size
        self.index = index
        self.offset = offset
        self.info = {}

    def update_info(self, service, info):
        lock.acquire()
        self.info[service] = info
        lock.release()

    def dump(self):
        return {
            "size": self.size,
            "index": self.index,
            "offset": self.offset,
            "info": self.info
        }
