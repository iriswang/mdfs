import urllib2
import numpy as np
import cStringIO
from node import Node
from scipy.misc import imread, imsave
import base64
import json
import requests

from base64 import b64encode

URL = "https://api.imgur.com/3/upload.json"

ZELDA = imread('nodes/img/zelda.png').flatten().tolist()

class ImgurNode(Node):

    name = 'imgur'
    client_id = '3eb3187308378ee'
    client_secret = '3cf14acc1c073c146a4520ef3cb26c2b113a0545'

    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        image = [ord(x) for x in chunk.data]
        if (len(chunk.data) < 10240):
            image.extend([0] * (10240 - len(chunk.data)))

        new_img =  [x ^ y for x, y in zip(ZELDA, image)]
        io_image = cStringIO.StringIO()
        imsave(io_image, np.array(new_img).reshape((80, 128)), format='png')

        headers = {"Authorization": "Client-ID " + self.client_id}
        result = requests.post(
            URL,
            headers = headers,
            data = {
                'image': b64encode(io_image.getvalue()),
                'type': 'base64',
                'name': 'testing123.png',
                'title': 'First Test'
            }
        )
        chunk.update_info("imgur", {
            "link": result.json()['data']['link']
        })
        self.get_chunk_data(chunk)


    def get_chunk_data(self, chunk):
        link = chunk.info['imgur']['link']
        img = cStringIO.StringIO(urllib2.urlopen(link).read())
        new_img = imread(img).flatten().tolist()
        new_img =  [x ^ y for x, y in zip(new_img, ZELDA)]
        new_img = new_img[:chunk.size]
        chunk.data = bytearray(new_img)
