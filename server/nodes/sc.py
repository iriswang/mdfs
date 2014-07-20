import wave, random, struct, soundcloud
from node import Node
import logging
import urllib2
import requests
import cStringIO

logging.basicConfig(filename='soundcloud.log',level=logging.DEBUG)


class SoundCloudNode(Node):

    name = 'soundcloud'
    client_id = 'd3d8d0b3e2db7a1085678bd9478024dd'
    client_secret = 'db9de01a71abe026ba8cbef27373a21b'

    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        access_token = '1-88843-105197285-dfa6baca3aa6e2'

        melody = [ord(x) for x in chunk.data]
        self.make_melody(melody)
        # create a client object with access token
        client = soundcloud.Client(access_token=access_token)


        # upload audio file
        track = client.post('/tracks', track={
            'title': 'MDFS',
            'asset_data': open('temp.wav', 'rb'),
            "downloadable": "true",
            "sharing": 'private'
        })

        chunk.update_info("soundcloud", {
            "link": track.download_url
        })

        import time
        # really ghetto
        time.sleep(10)

        # temp = self.get_chunk_data(chunk)

        # if bytearray(melody) == temp:
        #     logging.info('ITS THE SAME')

    def get_chunk_data(self, chunk):
        access_token = '1-88843-105197285-dfa6baca3aa6e2'
        client_id = 'd3d8d0b3e2db7a1085678bd9478024dd'

        # logging.info(chunk.info['soundcloud']['link']+"?access_token=%s&client_id=%s" % (self.access_token, client_id))
        # params = {
        #     "access_token": self.access_token,
        #     "client_id": client_id
        # }
        link = chunk.info['soundcloud']['link']+"?access_token=%s&client_id=%s" % (access_token, client_id)
        r = requests.get(link, stream=True)
        if r.status_code == 200:
            iostream = cStringIO.StringIO()
            for c in r.iter_content():
                iostream.write(c)
            data = iostream.getvalue()
        else:
            raise Exception("THIS IS REALLY BAD: 404")

        # output it to a file so its a wave file
        output = open("output.wav", "w")
        output.write(data)
        output.close()

        rst = []
        waveFile = wave.open("output.wav", "r")
        length = waveFile.getnframes()
        for i in range(0,length):
            waveData = waveFile.readframes(1)
            rst.append(struct.unpack("hh", waveData)[0])
        return bytearray(rst)


    def make_melody(self, melody):
        noise_output = wave.open('temp.wav', 'w')
        noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))

        values = []
        for i in melody:
            packed_value = struct.pack('h', int(i))
            values.append(packed_value)
            values.append(packed_value)

        value_str = ''.join(values)
        noise_output.writeframes(value_str)

        noise_output.close()

