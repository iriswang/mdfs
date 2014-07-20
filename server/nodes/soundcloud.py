import wave, random, struct, soundcloud

class SoundCloudNode(Node):

    client_id = 'd3d8d0b3e2db7a1085678bd9478024dd'
    client_secret = 'db9de01a71abe026ba8cbef27373a21b'

    def __init__(self, access_token):
        Node.__init__(self, access_token)

    def put_chunk_data(self, chunk):
        self.access_token = '1-88843-105197285-dfa6baca3aa6e2'


        melody = [ord(x) for x in chunk.data]

        # create a client object with access token
        client = soundcloud.Client(access_token=self.access_token)

        make_noise()
        # upload audio file
        track = client.post('/tracks', track={
            'title': 'This is my sound',
            'asset_data': open('testing.wav', 'rb')
        })

        # print track link
        
        chunk.update_info("soundcloud", {
            "link": track.permalink_url
        })
        print track.permalink_url
        self.get_chunk_data(chunk)

    def get_chunk_data(self, chunk):
        
        assert chunk.data == bytearray(new_img)


def make_noise():
    import wave, random, struct
    # noise_output = str()
    noise_output = wave.open('testing.wav', 'w')
    noise_output.setparams((2, 2, 11000, 0, 'NONE', 'not compressed'))

    values = []
    SAMPLE_LEN = 132300
    for i in range(0, SAMPLE_LEN):
            value = random.randint(-128, 128)
            
            packed_value = struct.pack('h', value)
            values.append(packed_value)
            values.append(packed_value)

    value_str = ''.join(values)
    noise_output.writeframes(value_str)

    noise_output.close()
