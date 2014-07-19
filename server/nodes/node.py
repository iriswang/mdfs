class Node:

    def get_chunk_data(self, chunk):
        raise NotImplementedError

    def put_chunk_data(self, data, id):
        raise NotImplementedError
