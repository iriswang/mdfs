from dropbox.client import DropboxClient
from dropbox import rest
import base64
from node import Node
import hashlib



class DBNode(Node):

    name = 'dropbox'
    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        access_token = "JkT9Fsx17gQAAAAAAAAAs1DAbvAU3sQrP1pJ8WiTdnG7HzQHE70idZ9Ph-GBuA3s"
        hash = hashlib.md5(chunk.data)
        path = '/' + hash.hexdigest()
        client = DropboxClient(access_token)
        try:
            response = client.metadata(path)
            if 'is_deleted' in response and response['is_deleted']:
                response = client.put_file('/' + path, base64.b64encode(chunk.data))
        except rest.ErrorResponse as e:
            if e.status == 404:
                response = client.put_file('/' + path, base64.b64encode(chunk.data))
        chunk.update_info('dropbox', response['path'] )

    def get_chunk_data(self, chunk):
        access_token = "JkT9Fsx17gQAAAAAAAAAs1DAbvAU3sQrP1pJ8WiTdnG7HzQHE70idZ9Ph-GBuA3s"
        client = DropboxClient(access_token)
        f, response = client.get_file_and_metadata(chunk.info['dropbox'])
        chunk.data = base64.b64decode(f.read())

