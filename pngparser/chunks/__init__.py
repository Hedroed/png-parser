from typing import Any, Optional

from ..chunktypes import (CHUNK_LENGTH_SIZE, TYPE_IDAT, TYPE_IEND, TYPE_IHDR,
                          TYPE_PLTE, TYPE_iTXt, TYPE_pHYs, TYPE_tEXt,
                          TYPE_tIME, TYPE_zTXt)
from ..color import Color
from .bkgd import ChunkBkgd
from .ihdr import ChunkIHDR
from .phys import ChunkPhys
from .plte import ChunkPLTE
from .text import ChunkText
from .time import ChunkTime
from .ztxt import ChunkZtxt


class ChunkRaw:
    def __init__(self, type_: bytes, data: bytes, crc: Optional[bytes] = None) -> None:
        self.type = type_
        self.data = data
        self.crc = crc or b'\x00\x00\x00\x00'

    def to_bytes(self) -> bytes:
        length = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return length + self.type + self.data + self.crc

    def __str__(self) -> str:
        return f'Chunk({Color.text}{self.data!r}{Color.r})'


FACTORY = {
    TYPE_IHDR: ChunkIHDR,
    TYPE_PLTE: ChunkPLTE,
    TYPE_IDAT: ChunkRaw,
    TYPE_IEND: ChunkRaw,
    TYPE_tEXt: ChunkText,
    TYPE_iTXt: ChunkRaw,
    TYPE_zTXt: ChunkZtxt,
    TYPE_tIME: ChunkTime,
    TYPE_pHYs: ChunkPhys,
}


def create_chunk(chunk_type: bytes, data: bytes, crc: bytes) -> Any:
    if chunk_type in FACTORY:
        return FACTORY[chunk_type](chunk_type, data, crc)
    return ChunkRaw(chunk_type, data, crc)
