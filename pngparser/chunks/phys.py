import struct

from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE


class ChunkPhys:
    def __init__(self, type_: bytes, data: bytes, crc: bytes) -> None:
        self.type = type_
        self.crc = crc

        values = struct.unpack('>IIB', data)
        self.px_per_unit_x = values[0]
        self.px_per_unit_y = values[1]
        self.unit = values[2]

    @property
    def data(self) -> bytes:
        return struct.pack('>IIB',
                           self.px_per_unit_x,
                           self.px_per_unit_y,
                           self.unit)

    def to_bytes(self) -> bytes:
        length = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return length + self.type + self.data + self.crc

    def __str__(self) -> str:
        unit = 'meter' if self.unit == 1 else 'unknown'
        return '{0.text}Physical: {1.px_per_unit_x} pixels per {2} for X, ' \
               '{1.px_per_unit_y} pixels per {2} for Y{0.r}'.format(Color, self, unit)
