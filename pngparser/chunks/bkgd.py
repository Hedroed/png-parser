from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE


class ChunkBkgd:
    def __init__(self, type_: bytes, data: bytes, crc: bytes) -> None:
        self.type = type_
        self.data = data
        self.crc = crc

    def to_bytes(self) -> bytes:
        length = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return length + self.type + self.data + self.crc

    def __str__(self) -> str:
        return f'bkGd({Color.text}{self.data!r}{Color.r})'
