import struct

from ..utils import pixel_type_to_length
from ..color import Color
from ..chunktypes import CHUNK_LENGTH_SIZE

COLOR_TYPE = {
    '0': ([1, 2, 4, 8, 16], 'Each pixel is a grayscale sample.'),
    '2': ([8, 16], 'Each pixel is an R,G,B triple.'),
    '3': ([1, 2, 4, 8], 'Each pixel is a palette index; a PLTE chunk must appear.'),
    '4': ([8, 16], 'Each pixel is a grayscale sample, followed by an alpha sample.'),
    '6': ([8, 16], 'Each pixel is an R,G,B triple, followed by an alpha sample.')
}

COLOR_TYPE_GRAYSCALE = 0
COLOR_TYPE_RGB = 2
COLOR_TYPE_PALETTE = 3
COLOR_TYPE_ALPHAGRAY = 4
COLOR_TYPE_RGBA = 6


class ChunkIHDR:
    def __init__(self, type_: bytes, data: bytes, crc: bytes) -> None:
        self.type = type_
        self.crc = crc

        values = struct.unpack('>IIBBBBB', data)

        self.width = values[0]
        self.height = values[1]
        self.bit_depth = values[2]
        self.color_type = values[3]
        self.compression_method = values[4]
        self.filter_method = values[5]
        self.interlace_method = values[6]

        self.color_type_display = ''  # Initialize variable
        self.check_color_type()

    def check_color_type(self) -> None:
        color_type = str(self.color_type)
        if color_type in COLOR_TYPE:
            color = COLOR_TYPE[color_type]

            if self.bit_depth not in color[0]:
                print(f'{Color.unknown}Bit depth no allowed in color type{Color.r}')

            self.color_type_display = f'Code = {self.color_type} ; Depth Allow = {color[0]} ; {color[1]}'

    def use_palette(self) -> bool:
        return self.color_type == COLOR_TYPE_PALETTE

    @property
    def pixel_len(self) -> int:
        """
        Get number of bytes per pixel.

        Computed from color_type attribute.
        """
        return pixel_type_to_length(self.color_type)

    @property
    def data(self) -> bytes:
        return struct.pack('>IIBBBBB',
                           self.width,
                           self.height,
                           self.bit_depth,
                           self.color_type,
                           self.compression_method,
                           self.filter_method,
                           self.interlace_method)

    def to_bytes(self) -> bytes:
        length = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return length + self.type + self.data + self.crc

    def __str__(self) -> str:
        ret = '{0.text} - Width : {0.id}{1.width}{0.r}\n' \
              '{0.text} - Height : {0.id}{1.height}{0.r}\n' \
              '{0.text} - Bit depth : {0.id}{1.bit_depth}{0.r}\n' \
              '{0.text} - Color type : {0.id}{1.color_type_display}{0.r}\n' \
              '{0.text} - Compression method : {0.id}{1.compression_method}{0.r}\n' \
              '{0.text} - Filter method : {0.id}{1.filter_method}{0.r}\n' \
              '{0.text} - Interlace method : {0.id}{1.interlace_method}{0.r}\n'.format(Color, self)
        return ret
