from typing import Any

from ..color import Color

from ..chunktypes import *
from .ihdr import ChunkIHDR
from .plte import ChunkPLTE
from .phys import ChunkPhys
from .bkgd import ChunkBkgd
from .time import ChunkTime
from .text import ChunkText
from .ztxt import ChunkZtxt

FACTORY = {
    TYPE_IHDR: ChunkIHDR,
    TYPE_PLTE: ChunkPLTE,
    # TYPE_IDAT: ChunkIDAT,
    # TYPE_IEND: ChunkIend,
    TYPE_tEXt: ChunkText,
    # TYPE_iTXt: ChunkItxt,
    TYPE_zTXt: ChunkZtxt,
    TYPE_tIME: ChunkTime,
    TYPE_pHYs: ChunkPhys,
}


class ChunkRaw:
    def __init__(self, type_: bytes, data: bytes, crc: bytes=None):
        self.type = type_
        self.data = data
        self.crc = crc or b'\x00\x00\x00\x00'

    def to_bytes(self):
        l = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return l + self.type + self.data + self.crc

    def __str__(self):
        return f"Chunk({Color.text}{self.data!r}{Color.r})"


def create_chunk(chunk_type: bytes, data: bytes, crc: bytes) -> Any:
    if chunk_type in FACTORY:
        return FACTORY[chunk_type](chunk_type, data, crc)

    else:
        return ChunkRaw(chunk_type, data, crc)
