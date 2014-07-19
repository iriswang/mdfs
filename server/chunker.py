import multiprocessing as mp
import logging
logger = mp.log_to_stderr()

from nodes import get_nodes, Chunk

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
    node.put_chunk_data(chunk)


def allocate_chunks_to_service(chunks, n=2):
    chunk_store = []
    for chunk in chunks:
        nodes = get_nodes(chunk, REDUNDANCY)
        for node in nodes:
            chunk_store.append((node, chunk))
    pool.map(put_chunk, chunk_store)

pool = mp.Pool(10)

if __name__ == "__main__":
    data = open('../img/link.jpg', 'rb').read()
    chunks = split_bytes_into_chunks(data)
    allocate_chunks_to_service(chunks)
