from dropbox.client import DropboxClient
from dropbox import rest as dbrest
import base64
from node import Node
import hashlib



class DBNode(Node):

    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        access_token = "JkT9Fsx17gQAAAAAAAAAs1DAbvAU3sQrP1pJ8WiTdnG7HzQHE70idZ9Ph-GBuA3s"
        hash = hashlib.md5(chunk.data)
        client = DropboxClient(access_token)
        response = client.put_file('/' + hash.hexdigest(), base64.b64encode(chunk.data))
        chunk.update_info('dropbox', response['path'] )
