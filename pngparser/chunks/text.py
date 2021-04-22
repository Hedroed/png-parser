from ..color import Color

from ..chunktypes import CHUNK_LENGTH_SIZE


class ChunkText:
    def __init__(self, type_: bytes, data: bytes, crc: bytes):
        self.type = type_
        self.crc = crc
        try:
            key, text = data.split(b'\x00', 1)
            self.key = key.decode('utf-8', 'replace')
            self.text = text.decode('utf-8', 'replace')
        except ValueError:
            self.key = None
            self.text = data.decode('utf-8', 'replace')

    @property
    def data(self):
        if self.key:
            return self.key.encode() + b'\x00' + self.text.encode()
        else:
            return self.text.encode()

    def to_bytes(self):
        l = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return l + self.type + self.data + self.crc

    def __repr__(self):
        return f"ChunkDataText({self.key}: {self.text})"

    def __str__(self):
        return f"{Color.text}{self.key}: {self.text}{Color.r}"
