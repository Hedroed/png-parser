from .image import Image
from .utils import BitArray
from .pixel import Pixel

class ImageData():
    def __init__(self, header, scanlines, palette=None):
        self.header = header
        
        if palette:
            color_type = self.header.color_type
            self.palette = [Pixel(color_type, px) for px in palette.palette]
        else:
            self.palette = None

        self.image = Image(header.color_type, header.width, len(scanlines))

        self.rows = []
        for y, row in enumerate(scanlines):
            pixels = self._loadPixels(row)

            image_row = ImageDataRow(row[0], pixels, header.color_type, y, self.image)
            self.rows.append(image_row)

    def show(self):
        self.image.show()

    def save_to_bytes(self):
        ret = b''
        for row in self.rows:
            raw = self._savePixels(row)
            ret += row.filter.to_bytes(1, 'big') + raw

        return ret

    def __bytes__(self):
        return self.save_to_bytes() 

    def _loadPixels(self, row):
        pixels = []
        pxLen = self.header.pixel_len
        color_type = self.header.color_type

        if self.palette:
            pixels = [self.palette[row[i]] for i in range(1, len(row))]
        else:
            px = []
            bit_depth = self.header.bit_depth
            for val in BitArray(row[1:], bit_depth):
                if bit_depth != 8:
                    val = val * (2**bit_depth - 1)
                px.append(val)
                if len(px) == pxLen:
                    pixels.append(Pixel(color_type, px))
                    px = []

        return pixels

    def _savePixels(self, row_data):
        # bit_depth
        row_ret = b''
        # px_ok = 0
        # px_ko = 0
        if self.palette:
            for px in row_data.pixels:
                if px in self.palette:
                    idx = self.palette.index(px)
                    row_ret += idx.to_bytes(1, 'big')
                    # px_ok += 1
                else:
                    # print("[!] Missing pixel %s in palette" % px)
                    # px_ko += 1
                    row_ret += px[0].to_bytes(1, 'big')
            # print("[!] ok:%d ko:%d sum:%d" % (px_ok, px_ko, px_ok+px_ko))

        else:
            for px in row_data.pixels:
                row_ret += px.to_bytes()

        return row_ret


class ImageDataRow():
    def __init__(self, filter_, pixels, color_type, y, image):
        self.filter = filter_
        self.pixels = pixels
        self.y = y
        self.color_type = color_type
        self.image = image

    def update_filter(self, new_filter:int):
        self._computePixels()

        if self.filter == new_filter:
            return

        new_pixels = []
        self.filter = new_filter
        for x, _ in enumerate(self.pixels):
            pixel = self._setpixelfilter(x, self.y, self.image)
            new_pixels.append(pixel)

        self.pixels = new_pixels


    def _computePixels(self):
        for x, px in enumerate(self.pixels):
            pixel = self._getpixelfilter(x, self.y, px, self.image)
            self.image.putpixel((x, self.y), pixel)

    def _getpixelSafe(self, image, x, y):
        try:
            return image.getpixel((x, y))
        except IndexError:
            return Pixel(self.color_type)

    def _getpixelfilter(self, x, y, pixel, image):
        leftPixel = self._getpixelSafe(image, x - 1, y)
        upPixel = self._getpixelSafe(image, x, y - 1)
        cornerPixel = self._getpixelSafe(image, x - 1, y - 1)

        if self.filter == 1:
            pixel = pixel + leftPixel

        elif self.filter == 2:
            pixel = pixel + upPixel

        elif self.filter == 3:
            pixel = pixel.addMean(leftPixel, upPixel)

        elif self.filter == 4:
            bestPixel = Pixel.peath(leftPixel, upPixel, cornerPixel)
            pixel = pixel + bestPixel

        return pixel

    def _setpixelfilter(self, x, y, image):
        leftPixel = self._getpixelSafe(image, x - 1, y)
        upPixel = self._getpixelSafe(image, x, y - 1)
        cornerPixel = self._getpixelSafe(image, x - 1, y - 1)
        pixel = self._getpixelSafe(image, x, y)

        ret = pixel
        if self.filter == 1:
            ret = pixel - leftPixel

        elif self.filter == 2:
            ret = pixel - upPixel

        elif self.filter == 3:
            ret = pixel.subMean(leftPixel, upPixel)

        elif self.filter == 4:
            bestPixel = Pixel.peath(leftPixel, upPixel, cornerPixel)
            ret = pixel - bestPixel

        return ret
