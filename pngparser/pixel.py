from .utils import pixel_type_to_length
from .chunkdata import ChunkDataIHDR


class Pixel():
    def __init__(self, type_, values=[]):
        self.type = type_

        values_count = len(values)
        if values_count == 0:  # No values is empty pixel
            values_count = 4
            values = [0, 0, 0, 0]

        self.px_len = pixel_type_to_length(type_)
        if type_ == ChunkDataIHDR.COLOR_TYPE_PALETTE:
            if values_count < 3:
                raise Exception("Bad pixel values count %d, must be 3 for colormap" % (values_count))
            else:
                self.px_len = 3
        elif values_count < self.px_len:
            raise Exception("Bad pixel values count %d, must be %d" % (values_count, self.px_len))

        self.values = tuple(values[0:self.px_len])

    def __add__(self, other):
        if self.type != other.type:
            raise Exception("Invalid type %s and %s" % (self.type, other.type))

        px = []
        for i in range(len(other)):
            px.append((self[i] + other[i]) % 256)

        return Pixel(self.type, px)

    def __sub__(self, other):
        if self.type != other.type:
            raise Exception("Invalid type %s sub %s" % (self.type, other.type))

        px = []
        for i in range(len(other)):
            px.append((self[i] - other[i]) % 256)

        return Pixel(self.type, px)

    def addMean(self, a, b):
        if not(self.type == a.type and a.type == b.type):
            raise Exception("Invalid type %s, %s, %s" % (self.type, a.type,
                                                         b.type))
        px = []
        for i in range(len(self)):
            px.append((self[i] + ((a[i] + b[i]) // 2)) % 256)

        return Pixel(self.type, px)

    def subMean(self, a, b):
        if not(self.type == a.type and a.type == b.type):
            raise Exception("Invalid type %s, %s, %s" % (self.type, a.type,
                                                         b.type))
        px = []
        for i in range(len(self)):
            px.append((self[i] - ((a[i] + b[i]) // 2)) % 256)

        return Pixel(self.type, px)

    # def getTuple(self):
    #     return self.values

    def to_bytes(self):
        return bytearray(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __eq__(self, other):
        if self.type != other.type:
            return False
        ret = True
        for a, b in zip(self.values, other.values):
            ret &= a == b
        return ret

    def __len__(self):
        return self.px_len

    def __repr__(self):
        return "Pixel %s" % (self.values,)

    @staticmethod
    def peath(a, b, c):
        if not(a.type == b.type and b.type == c.type):
            raise Exception("Invalid type %s, %s, %s" %
                            (a.type, b.type, c.type))

        ret = []

        pxs = [a, b, c]
        for i in range(len(a)):
            tmp = a[i] + b[i] - c[i]

            proximity = [abs(tmp - px[i]) for px in pxs]
            minval = min(*proximity)
            pxIndex = proximity.index(minval)

            ret.append(pxs[pxIndex][i])

        return Pixel(a.type, ret)
