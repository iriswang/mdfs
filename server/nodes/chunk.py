from multiprocessing import Lock

lock = Lock()

class Chunk:

    def __init__(self, data, size, index, offset, info={}):
        self.data = data
        self.size = size
        self.index = index
        self.offset = offset
        self.info = info

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

    @staticmethod
    def load(json):
        return Chunk(None, json['size'], json['size'], json['index'], json['offset'], json['info'])
