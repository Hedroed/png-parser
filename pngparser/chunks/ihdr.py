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

    def __init__(self, type_: bytes, data: bytes, crc: bytes):
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

        self.checkColorType()

    def checkColorType(self):
        c = str(self.color_type)
        if c in COLOR_TYPE:
            color = COLOR_TYPE[c]

            if self.bit_depth not in color[0]:
                print(f'{Color.unknown}Bit depth no allowed in color type{Color.r}')

            self.color_type_display = f'Code = {self.color_type} ; Depth Allow = {color[0]} ; {color[1]}'

    def use_palette(self):
        return self.color_type == COLOR_TYPE_PALETTE

    @property
    def pixel_len(self) -> int:
        """
        Get number of bytes per pixel.

        Computed from color_type attribute.
        """
        return pixel_type_to_length(self.color_type)

    @property
    def data(self):
        return struct.pack('>IIBBBBB',
                           self.width,
                           self.height,
                           self.bit_depth,
                           self.color_type,
                           self.compression_method,
                           self.filter_method,
                           self.interlace_method)

    def to_bytes(self):
        l = len(self.data).to_bytes(CHUNK_LENGTH_SIZE, 'big')
        return l + self.type + self.data + self.crc

    def __str__(self):
        ret = ""

        ret += "%s - %s : %s%s%s\n" % (Color.text,
                                       "Width", Color.id, self.width, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text,
                                       "Height", Color.id, self.height, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text,
                                       "Bit depth", Color.id, self.bit_depth, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Color type",
                                       Color.id, self.color_type_display, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Compression method",
                                       Color.id, self.compression_method, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Filter method",
                                       Color.id, self.filter_method, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Interlace method",
                                       Color.id, self.interlace_method, Color.r)

        return ret
