from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE

class ChunkBkgd:
    def __init__(self, type_: bytes, data: bytes, crc: bytes):
        self.type = type_
        self.data = data
        self.crc = crc

    def to_bytes(self):
        l = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return l + self.type + self.data + self.crc

    def __str__(self):
        return f"bkGd({Color.text}{self.data!r}{Color.r})"
