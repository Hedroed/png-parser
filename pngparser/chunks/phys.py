import struct

from ..color import Color


class ChunkPhys:
    def __init__(self, type_: bytes, data: bytes, crc: bytes):
        self.type = type_
        self.crc = crc

        values = struct.unpack('>IIB', data)
        self.px_per_unit_x = values[0]
        self.px_per_unit_y = values[1]
        self.unit = values[2]

    @property
    def data(self):
        return struct.pack('>IIB',
                           self.px_per_unit_x,
                           self.px_per_unit_y,
                           self.unit)

    def to_bytes(self):
        l = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return l + self.type + self.data + self.crc

    def __str__(self):
        unit = "meter" if self.unit == 1 else "unknown"
        return (f"{Color.text}Physical: {self.px_per_unit_x} pixels per {unit} for X, "
                f"{self.px_per_unit_y} pixels per {unit} for Y{Color.r}")
