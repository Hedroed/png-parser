import zlib
from PIL import Image
from mmap import ACCESS_READ, mmap
import os
import logging
from typing import List, Optional, Tuple

from .chunktypes import CHUNK_CRC_SIZE, CHUNK_LENGTH_SIZE, CHUNK_TYPE_SIZE, is_text_chunk, TYPE_IHDR
from .chunks import create_chunk, ChunkRaw
from .chunktypes import *
from .color import Color
from .imagedata import ImageData

PNG_MAGIC_NUMBER = b'\x89PNG\r\n\x1a\n'
PNG_MAGIC_NUMBER_SIZE = len(PNG_MAGIC_NUMBER)


class PngParser():
    def __init__(self, file):

        if type(file) == str:
            logging.debug("opening file %s", file)
            self.file = open(file, 'rb')

        else:
            logging.debug("read data")
            self.file = file

        # check file header
        if self.file.read(PNG_MAGIC_NUMBER_SIZE) != PNG_MAGIC_NUMBER:
            raise Exception(f'"{self.file.name}" file is not a PNG !')

        # load the picture to memory
        mm = mmap(self.file.fileno(), 0, access=ACCESS_READ)
        # skip file header
        mm.seek(PNG_MAGIC_NUMBER_SIZE, os.SEEK_SET)

        self.chunks: List[Chunk] = []
        self.chunks_pos: List[Tuple[int, int]] = []
        self.reader = mm

        self._readChunk()
        if all(c.type != TYPE_IHDR for c in self.chunks):
            logging.warning('found no header chunk')

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        if type_:
            logging.error("png error %s : %s\n%s", type_, value, traceback)

        self.close()

    def close(self):
        logging.debug("closing file")
        self.file.close()

    def _readChunk(self):
        position = 0
        while True:
            # read data length
            length_byte = self.reader.read(CHUNK_LENGTH_SIZE)

            if not length_byte:
                break

            chunk_length = int.from_bytes(length_byte, byteorder='big')

            chunk_type = self.reader.read(CHUNK_TYPE_SIZE)
            data = self.reader.read(chunk_length)
            crc = self.reader.read(CHUNK_CRC_SIZE)

            self.chunks_pos.append((position, self.reader.tell()-1))
            position = self.reader.tell()

            current_chunk = create_chunk(chunk_type, data, crc)
            logging.debug("found chunk %s", current_chunk.type)
            self.chunks.append(current_chunk)

    def show_image(self):

        img = self.get_image_data()
        img.show()

    def get_header(self):
        return next(c for c in self.chunks if c.type == TYPE_IHDR)

    def get_image_data(self) -> Optional[ImageData]:
        header_chunk = self.get_header()

        data = b''.join(c.data for c in self.chunks if c.type == TYPE_IDAT)
        if not data:
            return None

        try:
            logging.debug('deflate all data')
            data = zlib.decompress(data)
        except Exception:
            logging.exception('error in data decompression')
            raise
        else:
            header = header_chunk

            data_length = len(data)
            logging.debug("%d decompressed byte data loaded", data_length)

            # If palette
            palette = None
            if header.use_palette():
                logging.debug("use palette")
                palette = next(c for c in self.chunks if c.type == TYPE_PLTE)

            img = ImageData(header, data, palette=palette)

            return img

    def set_image_data(self, img: ImageData):
        data = img.to_bytes()

        compressed_data = zlib.compress(data)
        # new_chunk_size = len(compressed_data)

        new_idat = ChunkRaw(TYPE_IDAT, compressed_data, None)

        new_inserted = False
        new_chunks = []
        for chunk in self.chunks:
            if chunk.type == TYPE_IDAT:
                if not new_inserted:
                    new_inserted = True
                    new_chunks.append(new_idat)
            else:
                new_chunks.append(chunk)

        self.chunks = new_chunks
        for c in self.chunks:
            logging.debug("new chunks: %s", c.type)

    def save_file(self, path):

        with open(path, 'wb') as f:
            f.write(PNG_MAGIC_NUMBER)

            for chunk in self.chunks:
                # update chunk crc
                chunk.crc = zlib.crc32(chunk.type + chunk.data).to_bytes(CHUNK_CRC_SIZE, 'big')
                f.write(chunk.to_bytes())

    def get_by_index(self, idx):
        if idx >= len(self.chunks):
            raise Exception(f'index {idx} too big')

        return self.chunks[idx]

    def get_by_type(self, typeChunk):
        return [item for item in self.chunks if item.type == typeChunk]

    def get_all(self):
        return self.chunks

    def get_text_chunks(self):
        return [i for i in self.chunks if is_text_chunk(i.type)]

    def get_pos(self, chunk: ChunkRaw) -> Tuple[int, int]:
        try:
            return self.chunks_pos[self.chunks.index(chunk)]
        except ValueError:
            return (0, 0)
