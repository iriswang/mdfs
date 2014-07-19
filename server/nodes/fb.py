from node import Node
import requests
import base64
import logging

logging.basicConfig(level=logging.DEBUG)

class FBNode(Node):

    BASE_URL="https://graph.facebook.com"

    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        access_token = "CAACEdEose0cBAIrfJeCzr8ddc4fhbXgTJZCxkzTPV6qMxLeEZCO8ZBXVp3VoFQxINaIfRkp6eMl3ZBaSO8Mba7gmbipE8m3A7RwjIdtBZC3rzRn5ZCcvmHwPv8g4BsSXWSHfuyIj50vK87XZAbec9zlt6HGVuy4K1PNNZAYgJe1oC9S3XsIQBN5z5Npl0db2iIkee6loIFFQhxuxaJbN821A"
        privacy = "{'value': 'SELF'}"
        print self.BASE_URL
        result = requests.post(self.BASE_URL+"/me/feed", params={
            'access_token': access_token
        }, data={
            "message": base64.b64encode(chunk.data)
        })
        print result.text
