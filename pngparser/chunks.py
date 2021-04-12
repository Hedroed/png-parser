import zlib

from .chunktypes import ChunkField, ChunkTypes
from .chunkdata import ChunkData, get_chunk_data


class Chunk:

    @staticmethod
    def parse(type_byte: bytes, data_byte: bytes, crc_byte: bytes):
        type_ = ChunkTypes.from_binary(type_byte)
        data = get_chunk_data(type_, data_byte)

        return Chunk(type_, data, crc_byte)

    def __init__(self, type_: ChunkTypes, data: ChunkData, crc: bytes = None):
        assert isinstance(data, ChunkData), "data ChunkData,  must be a ChunkData object"

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
