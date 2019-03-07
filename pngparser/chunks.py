import zlib

from .chunktypes import ChunkField, ChunkTypes
from .chunkdata import ChunkData

class Chunk:

    @staticmethod
    def parse(type_byte: bytes, data_byte: bytes, crc_byte: bytes):
        type_ = ChunkTypes.from_binary(type_byte)
        data = ChunkData.get_chunk_data(type_, data_byte)

        return Chunk(type_, data, crc_byte)


    def __init__(self, type_: ChunkTypes, data: ChunkData, crc: bytes=None):
        assert isinstance(data, ChunkData), "data must be a ChunkData object"

        self.type = type_
        self.data = data
        self.crc = crc

    def compute_crc(self):
        _type = self.type.to_bytes()
        raw = self.data.data
        return zlib.crc32(_type + raw).to_bytes(ChunkField.CRC.length(), 'big')

    def to_bytes(self):
        _type = self.type.to_bytes()
        raw = self.data.data

        crc = self.compute_crc()
        l = len(raw).to_bytes(ChunkField.DATA_LENGTH.length(), 'big')

        return l + _type + raw + crc

    def __bytes__(self):
        return self.to_bytes()

    @property
    def length(self):
        return ChunkField.DATA_LENGTH.length() \
            + ChunkField.TYPE.length() \
            + len(self.data) \
            + ChunkField.CRC.length() \
            - 1

# Deprecated
class PNGChunks():
    """Contains all chunks and chunk access methods.
    """

    def __init__(self, chunks):
        self.chunks = {}

        for c in chunks:
            ctype = c.type.name
            if ctype not in self.chunks:
                self.chunks[ctype] = []
            self.chunks[ctype].append(c)

        self.header_index = 0
        self.palette_index = 0

        if ChunkTypes.IHDR.name in self.chunks:
            headers = self.chunks[ChunkTypes.IHDR.name]
            if headers and len(headers) > 1:
                print("%d headers find" % len(headers))
                index = int(input("Which headers use ? "))
                self.header_index = index

        if ChunkTypes.PLTE.name in self.chunks:
            palette = self.chunks[ChunkTypes.PLTE.name]
            if palette and len(palette) > 1:
                print("%d palettes find" % len(palette))
                index = int(input("Which palette use ? "))
                self.palette_index = index

    def getHeader(self):
        headers = self.chunks[ChunkTypes.IHDR.name]
        if headers and len(headers) > 0:
            return headers[self.header_index]

    def getData(self):
        data = self.chunks[ChunkTypes.IDAT.name]
        if data and len(data) > 0:
            return data

    def hasPalette(self):
        return ChunkTypes.PLTE.name in self.chunks

    def getPalette(self):
        if not self.hasPalette():
            return

        palette = self.chunks[ChunkTypes.PLTE.name]
        if palette and len(palette) > 0:
            return palette[self.palette_index]