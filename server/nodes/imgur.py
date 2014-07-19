from node import Node

class ImgurNode(Node):

    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        print "IMGUR", len(chunk.data)
