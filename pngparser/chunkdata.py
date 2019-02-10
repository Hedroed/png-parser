from PIL import Image
import struct
from datetime import datetime

from .chunktypes import ChunkTypes
from .color import Color
from .utils import pixel_type_to_length

class ChunkData:
    @staticmethod
    def get_chunk_data(chunk_type: ChunkTypes, data: bytes) -> "ChunkData":
        if chunk_type == ChunkTypes.IHDR:
            return ChunkDataIHDR(data)

        elif ChunkTypes.is_text_chunk(chunk_type):
            return ChunkDataText(data)

        elif chunk_type == ChunkTypes.PLTE:
            return ChunkDataPLTE(data)

        elif chunk_type == ChunkTypes.tIME:
            return ChunkDataTime(data)

        elif chunk_type == ChunkTypes.pHYs:
            return ChunkPhysical(data)

        else:
            return ChunkData(data)

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "AbstractChunkData(%s)" % self.data

    def __len__(self):
        return len(self.data)


class ChunkDataText(ChunkData):
    def __init__(self, data):
        self.data = data
        self.text = data.replace(b'\x00', b' ').decode('utf-8', 'replace')

    def __repr__(self):
        return "ChunkDataText(%s)" % self.data
        
    def __str__(self):
        return "%s%s%s" % (Color.text, self.text, Color.r)


class ChunkDataTime(ChunkData):
    def __init__(self, data):
        self.data = data

        values = struct.unpack('>HBBBBB', data)
        self.date = datetime(*values)


    def __str__(self):
        return "%sDate: %s%s" % (Color.text,
                                 self.date.strftime("%c"),
                                 Color.r)


class ChunkPhysical(ChunkData):
    def __init__(self, data):
        self.data = data

        values = struct.unpack('>IIB', data)

        self.px_per_unit_x = values[0]
        self.px_per_unit_y = values[1]
        self.unit = values[2]

    def __str__(self):
        unit = "meter" if self.unit == 1 else "unknown"
        return "%sPhysical: %d pixels per %s for X, %d pixels per %s for Y%s" % (Color.text,
                                                                                 self.px_per_unit_x, unit,
                                                                                 self.px_per_unit_y, unit,
                                                                                 Color.r)


class ChunkBackground(ChunkData):
    def __init__(self, data):
        self.data = data

        # TODO


class ChunkDataIDAT(ChunkData):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "%s%s%s" % (Color.text, self.data, Color.r)


class ChunkDataIHDR(ChunkData):
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

    def __init__(self, data):
        self.data = data

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
        if c in self.COLOR_TYPE:
            color = self.COLOR_TYPE[c]

            if self.bit_depth not in color[0]:
                print('%sBit depth no allowed in color type%s' %
                      (Color.unknown, Color.r))

            self.color_type_display = 'Code = %s ; Depth Allow = %s ; %s' % (
                self.color_type, color[0], color[1])

    def use_palette(self):
        return self.color_type == ChunkDataIHDR.COLOR_TYPE_PALETTE

    @property
    def pixel_len(self):
        return pixel_type_to_length(self.color_type)

    def __str__(self):
        ret = ""

        ret += "%s - %s : %s%s%s\n" % (Color.text,
                                       "Width", Color.id, self.width, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text,
                                       "Height", Color.id, self.height, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Bit depth",
                                       Color.id, self.bit_depth, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Color type",
                                       Color.id, self.color_type_display, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Compression method",
                                       Color.id, self.compression_method, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Filter method",
                                       Color.id, self.filter_method, Color.r)
        ret += "%s - %s : %s%s%s\n" % (Color.text, "Interlace method",
                                       Color.id, self.interlace_method, Color.r)

        return ret


class ChunkDataPLTE(ChunkData):
    def __init__(self, data):
        self.data = data

        self.palette = []
        for i in range(0, len(self.data), 3):
            rawPixel = self.data[i: i+3]
            pixel = (rawPixel[0], rawPixel[1], rawPixel[2])
            self.palette.append(pixel)

    def __str__(self):
        ret = "%s" % Color.text
        i = 0
        # print("%s%s%s" % (Color.text, self.data, Color.r))

        count = len(self.palette)
        size = 20
        width = 20
        height = ((count // 20) + 1)
        image = Image.new('RGB', (width * size, height * size))

        for k, px in enumerate(self.palette):
            x = k % width
            y = k // width

            for xx in range(size):
                for yy in range(size):
                    image.putpixel((xx + (x * size), yy + (y * size)), px)

        image.show()

        return "%s%s" % (ret, Color.r)
