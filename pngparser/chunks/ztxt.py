import zlib

from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE


class ChunkZtxt:
    def __init__(self, type_: bytes, data: bytes, crc: bytes) -> None:
        self.type = type_
        self.crc = crc

        key, rest = data.split(b'\x00', maxsplit=1)

        self.key = key.decode('utf-8')
        self.method = rest[0]
        self.text = zlib.decompress(rest[1:]).decode('utf-8', 'replace')
        self.data = self.text

    def to_bytes(self) -> bytes:
        data = bytearray()
        data += self.key.encode()
        data.append(0)
        data.append(self.method)
        data += zlib.compress(self.text.encode())

        length = len(data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return length + self.type + data + self.crc

    def __repr__(self) -> str:
        return f'ChunkZTxt({self.text})'

    def __str__(self) -> str:
        ret = '{0.text}Key : {0.data}{1.key}\n' \
              '{0.text}Text : {0.data}{1.text}\n' \
              '{0.text}Method : {0.data}{1.method}\n'.format(Color, self)
        return f'{ret}{Color.r}'
