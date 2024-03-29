from PIL import Image

from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE

PIXEL_LEN = 3


class ChunkPLTE:
    def __init__(self, type_: bytes, data: bytes, crc: bytes) -> None:
        self.type = type_
        self.crc = crc

        self.palette = []
        for i in range(0, len(data), PIXEL_LEN):
            pixel = tuple(data[i:i + PIXEL_LEN])
            self.palette.append(pixel)

    def to_bytes(self) -> bytes:
        length = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return length + self.type + self.data + self.crc

    def __getitem__(self, idx: int) -> tuple:
        return self.palette[idx]

    @property
    def data(self) -> bytes:
        ret = bytes()
        for pixel in self.palette:
            ret += bytes(pixel)
        return ret

    def __str__(self) -> str:
        size = 10
        width = 16
        height = len(self.palette) // width + 1
        image = Image.new('RGB', (width * size, height * size))

        for k, px in enumerate(self.palette):
            x = (k % width) * size
            y = (k // width) * size

            for xx in range(size):
                for yy in range(size):
                    image.putpixel((xx + x, yy + y), px)

        image.show()
        return f'{Color.text}{self.data!r}{Color.r}'
