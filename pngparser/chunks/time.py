import struct
import datetime

from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE


class ChunkTime:
    def __init__(self, type_: bytes, data: bytes, crc: bytes) -> None:
        self.type = type_
        self.crc = crc

        values = struct.unpack('>HBBBBB', data)
        self.datetime = datetime.datetime(*values)

    @property
    def data(self) -> bytes:
        return struct.pack('>HBBBBB',
                           self.datetime.year,
                           self.datetime.month,
                           self.datetime.day,
                           self.datetime.hour,
                           self.datetime.minute,
                           self.datetime.second)

    def to_bytes(self) -> bytes:
        length = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return length + self.type + self.data + self.crc

    def __str__(self) -> str:
        return '{0.text}Date: {1}{0.r}'.format(Color, self.datetime.strftime('%c'))
