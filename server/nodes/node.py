class Node:

    def get_chunk(self, id):
        raise NotImplementedError

    def put_chunk(self, chunk, id):
        raise NotImplementedError
