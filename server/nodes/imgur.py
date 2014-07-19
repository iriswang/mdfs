import numpy as np
import cStringIO
from node import Node
from scipy.misc import imread, imsave

class ImgurNode(Node):

    client_id = '3eb3187308378ee'
    client_secret = '3cf14acc1c073c146a4520ef3cb26c2b113a0545'

    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        image = [ord(x) for x in chunk.data]
        zelda = imread('nodes/img/zelda.png').flatten().tolist()
        if (len(chunk.data) < 10240):
            image.extend([0] * (10240 - len(chunk.data)))

        new_img =  [x + y for x, y in zip(zelda, image)]
        new_img =  [x - 255 if x > 255 else x for x in new_img]
        imsave('nodes/img/test.png', np.array(new_img).reshape((80, 128)))
        test_img = imread('nodes/img/test.png').flatten().tolist()
        test_img =  [x - y for x, y in zip(test_img, image)]
        test_img =  [x + 255 if x < 0 else x for x in test_img]
        imsave('nodes/img/test2.png', np.array(test_img).reshape((80, 128)))
