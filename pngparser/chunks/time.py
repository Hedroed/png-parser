import struct
import datetime

from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE


class ChunkTime:
    def __init__(self, type_: bytes, data: bytes, crc: bytes):
        self.type = type_
        self.crc = crc

        values = struct.unpack('>HBBBBB', data)
        self.datetime = datetime.datetime(*values)

    @property
    def data(self):
        return struct.pack('>HBBBBB',
                           self.datetime.year,
                           self.datetime.month,
                           self.datetime.day,
                           self.datetime.hour,
                           self.datetime.minute,
                           self.datetime.second)

    def to_bytes(self):
        l = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return l + self.type + self.data + self.crc

    def __str__(self):
        return f"{Color.text}Date: {self.datetime.strftime('%c')}{Color.r}"
