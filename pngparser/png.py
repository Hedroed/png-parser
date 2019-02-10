import zlib
from PIL import Image
from mmap import ACCESS_READ, mmap
import os
import logging
from typing import List

from .chunktypes import ChunkField
from .chunks import PNGChunks, Chunk
from .chunkdata import ChunkData
from .chunktypes import ChunkTypes
from .color import Color
from .loader import Loader
from .imagedata import ImageData
# from pixel import Pixel
# from utils import BitArray

PNG_MAGIC_NUMBER = b'\x89PNG\r\n\x1a\n'
PNG_MAGIC_NUMBER_LENGTH = len(PNG_MAGIC_NUMBER)


class PngParser():
    def __init__(self, file):

        if type(file) == str:
            logging.debug("[!] Open file")
            self.file = open(file, 'rb')

        else:
            logging.debug("[!] Read file")
            self.file = file

        # check file header
        if self.file.read(PNG_MAGIC_NUMBER_LENGTH) != PNG_MAGIC_NUMBER:
            raise Exception('"{}" file is not a PNG !'.format(self.file.name))

        # load the picture to memory
        mm = mmap(self.file.fileno(), 0, access=ACCESS_READ)
        # skip file header
        mm.seek(PNG_MAGIC_NUMBER_LENGTH, os.SEEK_SET)

        self.chunks: List[Chunk] = []
        self.reader = mm

        self._readChunk()
        # if all(c.type != ChunkTypes.IHDR for c in self.chunks):
        #     logging.debug('%s[!] No header chunk%s' % (Color.unknown, Color.r))

    def __enter__(self):
            return self

    def __exit__(self, type_, value, traceback):
        if type_:
            print("Error %s : %s\n%s" % (type_, value, traceback))

        self.close()

    def close(self):
        logging.debug("[!] Close file")
        self.file.close()

    def _readChunk(self):
        self.count = 0
        stop = False
        while not stop:
            # start_position = self.reader.tell()

            # read data length
            length_byte = self.reader.read(ChunkField.DATA_LENGTH.length())

            if length_byte == b"":
                stop = True
                break

            chunk_length = int.from_bytes(length_byte, byteorder='big')
            # read type
            type_ = self.reader.read(ChunkField.TYPE.length())
            # read data
            data = self.reader.read(chunk_length)
            # read crc
            crc = self.reader.read(ChunkField.CRC.length())

            try:
                current_chunk = Chunk.parse(type_, data, crc)
            except Exception as e:
                raise e
                return None
            else:
                logging.debug("[!] Found chunk %s" % (current_chunk.type))
                self.chunks.append(current_chunk)
                self.count += 1

    def show_image(self):

        img = self.get_image_data()
        img.show()


        # header = png.getHeader().data
        # if header:
        #     print("%sCreating image !!!%s" % (Color.text, Color.r))

        #     iType, pxLen = self.getImageType(header)

        #     data = self.loadIDAT(header, png.getData(), pxLen)

        #     h = header.height
        #     if data:
        #         h = len(data)

        #     image = Image.new(iType, (header.width, h))

        #     print('%sSize: %sx%s%s' %
        #           (Color.text, header.width, h, Color.r))
        #     loader = Loader(max=h)
        #     loader.draw()

        #     for y in range(h):
        #         loader.increase()
        #         loader.draw()

        #         pixels = []
        #         row = data[y]
        #         filterValue = row[0]

        #         if png.hasPalette():
        #             palette = png.getPalette().data
        #             pixels = [palette.palette[row[i]]
        #                       for i in range(1, len(row))]
        #         else:
        #             px = []
        #             for val in BitArray(row[1:], header.bit_depth):
        #                 if header.bit_depth != 8:
        #                     val = val * (2**header.bit_depth - 1)
        #                 px.append(val)
        #                 if len(px) == pxLen:
        #                     pixels.append(tuple(px))
        #                     px = []

        #         for x, px in enumerate(pixels):
        #             pixel = Pixel(header.color_type, px)
        #             pixel = self.getpixelfilter(filterValue,
        #                                         x, y,
        #                                         pixel,
        #                                         image,
        #                                         header.color_type)
        #             image.putpixel((x, y), pixel.getTuple())

        #     image.show()
        #     print()
        # else:
        #     print("%sCan't create image 'No header'%s" %
        #           (Color.unknown, Color.r))

    def get_header(self):
        header_chunk = next(c for c in self.chunks if c.type == ChunkTypes.IHDR)
        return header_chunk.data

    def get_image_data(self):
        idats = [ c for c in self.chunks if c.type == ChunkTypes.IDAT]
        header_chunk = next(c for c in self.chunks if c.type == ChunkTypes.IHDR)

        if len(idats) <= 0:
            return None
        data = b''
        for idat in idats:
            data += idat.data.data

        try:
            logging.debug('[!] Deflate all')
            data = zlib.decompress(data)
        except Exception:
            logging.error('%sError in data decompression !%s' %
                    (Color.unknown, Color.r))
        else:
            header = header_chunk.data

            data_length = len(data)
            logging.debug("[!] %d Bytes decompressed data" % data_length)

            # line_width = pixel_count_in_line * bytes_count_by_pixel + the_filter_byte
            line_width = header.width * header.pixel_len + 1
            logging.debug("[!] %d Bytes per scanline" % line_width)

            scanlines = [data[i:i + line_width] for i in
                            range(0, data_length, line_width)]

            # If palette
            palette = None
            if header.use_palette():
                logging.debug("[!] Use palette")
                palette_chunk = next(c for c in self.chunks if c.type == ChunkTypes.PLTE)
                palette = palette_chunk.data

            img = ImageData(header, scanlines, palette=palette)

            return img

    def set_image_data(self, img: ImageData):
        data = img.save_to_bytes()

        compressed_data = zlib.compress(data)
        # new_chunk_size = len(compressed_data)

        new_idat = Chunk(ChunkTypes.IDAT, ChunkData(compressed_data))

        new_inserted = False
        new_chunks = []
        for chunk in self.chunks:
            if chunk.type == ChunkTypes.IDAT:
                if not new_inserted:
                    new_inserted = True
                    new_chunks.append(new_idat)
            else:
                new_chunks.append(chunk)

        self.chunks = new_chunks
        for c in self.chunks:
            logging.debug("[!] New chunks: %s" % c.type)

    def save_file(self, path):

        with open(path, 'wb') as f:
            f.write(PNG_MAGIC_NUMBER)

            for chunk in self.chunks:
                f.write(bytes(chunk))

    def get_by_id(self, id_):
        if id_ >= len(self.chunks):
            raise Exception('ID too big')

        return [self.chunks[id_]]

    def get_by_type(self, typeChunk):
        if not ChunkTypes.contains(typeChunk):
            raise Exception('Type not exist')

        return [item for item in self.chunks if item.type == typeChunk]

    def get_all(self):
        return self.chunks

    def get_text_chunks(self):
        return [i for i in self.chunks if ChunkTypes.is_text_chunk(i.type)]
