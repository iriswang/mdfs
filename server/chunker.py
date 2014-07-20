import multiprocessing as mp
import logging
import memcache

logger = mp.log_to_stderr()
logging.basicConfig(level=logging.DEBUG)

from nodes import get_nodes, Chunk, init_nodes, get_node
mc = memcache.Client(["127.0.0.1:11211"])


CHUNK_SIZE = 10240
REDUNDANCY = 2

def split_bytes_into_chunks(bytes):
    offset, length = 0, len(bytes)
    index = 0
    chunks = []
    while offset < length:
        data = bytes[offset:offset + CHUNK_SIZE]
        chunk = Chunk(data, len(data), index, offset)
        chunks.append(chunk)
        offset, index = offset + CHUNK_SIZE, index + 1
    return chunks


def put_chunk(chunk_store):
    node, chunk = chunk_store
    print "PUTTING", node, chunk
    try:
        node.put_chunk_data(chunk)
    except:
        logging.exception("put failed")
    return (node, chunk)


def get_chunk(chunk_store):
    node, chunk = chunk_store
    print node, chunk
    try:
        node.get_chunk_data(chunk)
    except:
        logging.exception("get failed")
    return (node, chunk)

def get_chunks(chunk_list, access_tokens, inode_id):
    print "CHUNKLIST", chunk_list
    chunk_store = []
    for chunk in chunk_list:
        print "DOING MC"
        chunk.data = mc.get('inode_' + str(inode_id) + 'index_' + str(chunk.index))
        if chunk.data == None:
            for node in chunk.info.keys():
                chunk_store.append((get_node(node, access_tokens), chunk))
    print chunk_store
    dump = pool.map(get_chunk, chunk_store)
    for chunk in chunk_list:
        mc.set('inode_' + str(inode_id) + 'index_' + str(chunk.index), chunk.data)
        for node, c in dump:
            print "LOPING", node, c
            if node.name in chunk.info and c.offset == chunk.offset:
                chunk.data = c.data
    return chunk_list

def allocate_chunks_to_service(chunks, inode_id, n=2):
    chunk_store = []
    for chunk in chunks:
        print "CHUNK", chunk.data
        mc.set('inode_' + str(inode_id) + 'index_' + str(chunk.index), chunk.data)
        nodes = get_nodes(chunk, {"facebook": None, "dropbox": None, "imgur": None, "soundcloud": None}, REDUNDANCY)
        for node in nodes:
            chunk_store.append((node, chunk))
    print "DUMP"
    dump = pool.map(put_chunk, chunk_store)
    print "DUMP", dump
    for chunk in chunks:
        for node, c in dump:
            if node.name in chunk.info and c.offset == chunk.offset:
                chunk.info[node.name] = c.info[node.name]
    chunk_dump = map(lambda chunk: chunk.dump(), chunks)
    print "CHUNK_DUMP", chunk_dump
    return chunk_dump

pool = mp.Pool(10)


if __name__ == "__main__":
    #init_nodes({}, 5)
    data = open('nodes/img/link.jpg', 'rb').read()
    chunks = split_bytes_into_chunks(data)
    print allocate_chunks_to_service(chunks, 0)
