import multiprocessing as mp
import logging
logger = mp.log_to_stderr()
logging.basicConfig(level=logging.DEBUG)

from nodes import get_nodes, Chunk, init_nodes, get_node

CHUNK_SIZE = 10240
REDUNDANCY = 1


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
    print "PUTTING", node, chunk.data
    node.put_chunk_data(chunk)
    return (node, chunk)


def get_chunk(chunk_store):
    node, chunk = chunk_store
    print node, chunk
    node.get_chunk_data(chunk)
    return (node, chunk)

def get_chunks(chunk_list, access_tokens):
    chunk_store = []
    for chunk in chunk_list:
        for node in chunk.info.keys():
            chunk_store.append((get_node(node, access_tokens), chunk))
    dump = pool.map(get_chunk, chunk_store)
    for chunk in chunk_list:
        for node, c in dump:
            print "LOPING", node, c
            if c.offset == chunk.offset:
                chunk.data = c.data
    return chunk_list

def allocate_chunks_to_service(chunks, n=2):
    chunk_store = []
    for chunk in chunks:
        nodes = get_nodes(chunk, {"facebook": None, "dropbox": None, "imgur": None, "soundcloud": None}, REDUNDANCY)
        for node in nodes:
            chunk_store.append((node, chunk))
    print "DUMP"
    dump = pool.map(put_chunk, chunk_store)
    print "DUMP", dump
    for chunk in chunks:
        for node, c in dump:
            if c.offset == chunk.offset:
                chunk.info[node.name] = c.info[node.name]
    chunk_dump = map(lambda chunk: chunk.dump(), chunks)
    return chunk_dump

pool = mp.Pool(10)


if __name__ == "__main__":
    #init_nodes({}, 5)
    data = open('nodes/img/link.jpg', 'rb').read()
    chunks = split_bytes_into_chunks(data)
    print allocate_chunks_to_service(chunks)
