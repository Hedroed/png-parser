import zlib

from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE


class ChunkZtxt:

    def __init__(self, type_: bytes, data: bytes, crc: bytes):
        self.type = type_
        self.crc = crc

        key, rest = data.split(b'\x00', maxsplit=1)

        self.key = key.decode('utf-8')
        self.method = rest[0]
        self.text = zlib.decompress(rest[1:]).decode('utf-8', 'replace')

    def to_bytes(self):
        data = bytearray()
        data += self.key.encode()
        data.append(0)
        data.append(self.method)
        data += zlib.compress(self.text.encode())

        l = len(data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return l + self.type + data + self.crc

    def __repr__(self):
        return f"ChunkZTxt({self.text})"

    def __str__(self):
        ret = f"{Color.text}Key : {Color.data}{self.key}\n"
        ret += f"{Color.text}Text : {Color.data}{self.text}\n"
        ret += f"{Color.text}Method : {Color.data}{self.method}\n"

        return f"{ret}{Color.r}"
