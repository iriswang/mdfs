import random

from node import Node
from fb import FBNode
from drop import DBNode
from imgur import ImgurNode
from chunk import Chunk
from redis import Redis

redis_client = Redis(db=1)

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w > r:
         return c
      upto += w
   assert False, "Shouldn't get here"

SERVICES = [('facebook', 6206), ('dropbox', 2000)]
SERVICE_MAP = {
    'facebook': FBNode,
    'dropbox': DBNode
}

def get_nodes(chunk, access_token, n=2):
    nodes = []
    services = set()
    while len(nodes) < n:
        service = weighted_choice(SERVICES)
        if service not in services:
            services.add(service)
            nodes.append(SERVICE_MAP[service](access_token, redis_client))
    return nodes
