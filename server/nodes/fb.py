from node import Node
import requests
import base64
import logging

import multiprocessing as mp
import logging
logger = mp.log_to_stderr()
logging.basicConfig(level=logging.DEBUG)


class FBNode(Node):

    BASE_URL="https://graph.facebook.com"

    name = 'facebook'
    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        access_token = "CAACEdEose0cBAPcnPT3Kz6Yt1ZAaRz8nZBC6u9A1f04sB8CxlQmwYkYDLGS70KqCwiFTwZC7gHuf7y1pHsKdboCp0kSDdQUREjV4f9HyK2al1VTFtpfUtZCoD3q5ja1OUioLwjBDp5IaBdCBvCMkPbDZCtUCrf5lovSQ4eZCQve2lamyR3o5ig9HNmxbUwQmJPIxJMefnByEryn393HZBGC"
        album_id = "782330891819429"
        privacy = "{'value': 'SELF'}"
        data = open('nodes/img/photo.jpg', 'rb')
        result = requests.post(self.BASE_URL+"/%s/photos" % album_id, params={
            'access_token': access_token
        }, files={
            "source": data
        }, data={
            "message": base64.b64encode(chunk.data),
            "no_story": 'false'
        })
        print result.text
        print result.json()
        chunk.update_info('facebook', {
            "type": 'image',
            "id": result.json()['id']
        })

    def get_chunk_data(self, chunk):
        access_token = "CAACEdEose0cBAAi9N7wuZB4XhThmntkrStMdmlzwG10RXZC91uqn0kZBX7ZBiahKfqF5jYT486dWrKjAaqvSSD1oZAuhFn1AY6iBrZCZBe7SK5F76LuSSBh3cqLvTQzoud60HQm88n0uegg0ZAUMZBnbAJCTL5BVpzvTLfvKFMAqU9VhOZA5ECyLYx11LkGSxD3rut48GRwOExLcCUmleyQZCtH"
        result = requests.get(BASE_URL+"/%s" % chunk.info["facebook"]["id"])
