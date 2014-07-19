class Node:

    def __init__(self, access_token, redis):
        self.access_token = access_token
        self.redis = redis

    def get_chunk_data(self, chunk):
        raise NotImplementedError

    def put_chunk_data(self, data, id):
        raise NotImplementedError
