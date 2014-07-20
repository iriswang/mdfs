import random

from node import Node
from fb import FBNode
from drop import DBNode
from imgur import ImgurNode
from sc import SoundCloudNode
from chunk import Chunk

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w > r:
         return c
      upto += w
   assert False, "Shouldn't get here"

#SERVICES = [('soundcloud', 2000)]
SERVICES = [('imgur', 000), ('dropbox', 2000)]#, ('imgur', 2000)]
SERVICE_MAP = {
    #'facebook': FBNode,
     'dropbox': DBNode,
     #'imgur': ImgurNode,
    #'soundcloud': SoundCloudNode,
}

def get_nodes(chunk, access_tokens, n=2):
    nodes = []
    services = set()
    while len(nodes) < n:
        service = weighted_choice(SERVICES)
        if service not in services:
            services.add(service)
            nodes.append(SERVICE_MAP[service](access_tokens[service]))
    return nodes

def get_node(service, access_tokens):
    return SERVICE_MAP[service](access_tokens[service])

def init_nodes(redis, access_tokens, user_id):
    for service, _ in SERVICES:
        result = redis.get("%s_%s_initializated" % (user_id, service))
        if result is None or result == false:
            SERVICE_MAP[service](access_tokens[service]).init(redis)
            result = redis.set("%s_%s_initializated" % (user_id, service), )
