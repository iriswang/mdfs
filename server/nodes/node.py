class Node:

    def __init__(self, access_token):
        self.access_token = access_token

    def get_chunk_data(self, chunk):
        raise NotImplementedError

    def put_chunk_data(self, data):
        raise NotImplementedError

    def init(self, *args):
        pass
