import logging
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from .chunks import ChunkIHDR
# from .image import Image
# from .pixel import Pixel
from .utils import BitArray

_adam7 = ((0, 0, 8, 8),
          (4, 0, 8, 8),
          (0, 4, 4, 8),
          (2, 0, 4, 4),
          (0, 2, 2, 4),
          (1, 0, 2, 2),
          (0, 1, 1, 2))


def apply_filter(header: ChunkIHDR, filter_type: int, scanline: bytes, previous: Optional[bytes] = None) -> bytes:
    result = bytearray(scanline)

    if filter_type == 0:
        return result

    fu = max(1, header.pixel_len)

    if not previous:
        if filter_type == 2:  # up
            return result
        if filter_type == 3:  # average
            previous = [0]*len(scanline)
        elif filter_type == 4:  # "paeth"
            filter_type = 1

    elif len(previous) < len(scanline):
        previous += b'\x00' * (len(scanline) - len(previous))

    if filter_type == 1:  # sub
        ai = -fu
        for i, x in enumerate(scanline):
            if ai >= 0:
                x = (x - scanline[ai]) & 0xff
            result[i] = x
            ai += 1

    elif filter_type == 2:  # up
        for i, x in enumerate(scanline):
            x = (x - previous[i]) & 0xff
            result[i] = x

    elif filter_type == 3:  # average
        ai = -fu
        for i, x in enumerate(scanline):
            if ai >= 0:
                x = (x - ((scanline[ai] + previous[i]) >> 1)) & 0xff
            else:
                x = (x - (previous[i] >> 1)) & 0xff
            result[i] = x
            ai += 1

    elif filter_type == 4:  # paeth
        # http://www.w3.org/TR/PNG/#9Filter-type-4-Paeth
        ai = -fu  # also used for ci
        for i, x in enumerate(scanline):
            a = 0
            b = previous[i]
            c = 0

            if ai >= 0:
                a = scanline[ai]
                c = previous[ai]
            p = a + b - c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc:
                pr = a
            elif pb <= pc:
                pr = b
            else:
                pr = c

            x = (x - pr) & 0xff
            result[i] = x
            ai += 1
    return result


def undo_filter(header: ChunkIHDR, filter_type: int, scanline: bytes, previous: Optional[bytes] = None) -> bytearray:
    result = bytearray(scanline)

    if filter_type == 0:
        return result

    fu = max(1, header.pixel_len)

    if not previous:
        previous = [0]*len(scanline)

    if filter_type == 1:  # sub
        ai = 0
        for i in range(fu, len(result)):
            x = scanline[i]
            a = result[ai]
            result[i] = (x + a) & 0xff
            ai += 1

    elif filter_type == 2:  # up
        for i, _ in enumerate(result):
            x = scanline[i]
            b = previous[i]
            result[i] = (x + b) & 0xff

    elif filter_type == 3:  # average
        ai = -fu
        for i, _ in enumerate(result):
            x = scanline[i]
            if ai < 0:
                a = 0
            else:
                a = result[ai]
            b = previous[i]
            result[i] = (x + ((a + b) >> 1)) & 0xff
            ai += 1

    elif filter_type == 4:  # paeth
        ai = -fu
        for i, _ in enumerate(result):
            x = scanline[i]
            if ai < 0:
                a = c = 0
            else:
                a = result[ai]
                c = previous[ai]
            b = previous[i]
            p = a + b - c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc:
                pr = a
            elif pb <= pc:
                pr = b
            else:
                pr = c
            result[i] = (x + pr) & 0xff
            ai += 1
    return result

    # def _setpixelfilter(self, x, y, image):
    #     leftPixel = self._getpixelSafe(image, x - 1, y)
    #     upPixel = self._getpixelSafe(image, x, y - 1)
    #     cornerPixel = self._getpixelSafe(image, x - 1, y - 1)
    #     pixel = self._getpixelSafe(image, x, y)

    #     ret = pixel
    #     if self.filter == 1:
    #         ret = pixel - leftPixel

    #     elif self.filter == 2:
    #         ret = pixel - upPixel

    #     elif self.filter == 3:
    #         ret = pixel.subMean(leftPixel, upPixel)

    #     elif self.filter == 4:
    #         bestPixel = Pixel.peath(leftPixel, upPixel, cornerPixel)
    #         ret = pixel - bestPixel

    #     return ret


def deinterlace(header: ChunkIHDR, raw):
    """
    Read raw pixel data, undo filters, deinterlace, and flatten.
    Return in flat row flat pixel format.
    """

    source_offset = 0

    for xstart, ystart, xstep, ystep in _adam7:
        if xstart >= header.width:
            continue

        recon = None
        # Pixels per row (reduced pass image)
        ppr = int(math.ceil((header.width-xstart)/float(xstep)))

        # Row size in bytes for this pass.
        row_size = int(math.ceil(header.pixel_len * ppr))

        for _ in range(ystart, header.height, ystep):
            try:
                filter_type = raw[source_offset]
            except IndexError:
                logging.error('missing scanlines for interlaced image')
                return

            source_offset += 1
            scanline = raw[source_offset:source_offset+row_size]
            source_offset += row_size
            recon = undo_filter(header, filter_type, scanline, recon)
            # Convert so that there is one element per pixel value

            yield Scanline(filter_type, recon)


@dataclass
class Scanline:
    filter: int
    data: bytes


class ImageData:
    def __init__(self, header: ChunkIHDR, data: bytes, palette=None) -> None:
        self.header = header
        self.data = data

        if palette:
            self.palette = palette
        else:
            self.palette = None

        self._scanlines: Optional[List[Scanline]] = None

    def _load_scanlines(self) -> None:
        if self.header.interlace_method == 1:
            self._scanlines = list(deinterlace(self.header, self.data))
            logging.debug('%d interlaced scanlines loaded', len(self._scanlines))
        else:
            # line_width = pixel_count_in_line * bytes_count_by_pixel + the_filter_byte
            line_width = self.header.width * self.header.pixel_len
            logging.debug('%d bytes per scanline', line_width)

            recon = None
            self._scanlines = []

            cursor = 0
            while cursor < len(self.data):
                filter_type = self.data[cursor]
                cursor += 1
                data = self.data[cursor:cursor+line_width]
                cursor += line_width

                recon = undo_filter(self.header, filter_type, data, recon)

                scanline = Scanline(filter_type, recon)
                self._scanlines.append(scanline)

            logging.debug('%d scanlines loaded', len(self._scanlines))

    @property
    def scanlines(self) -> List[Scanline]:
        if self._scanlines is None:
            logging.debug('loading scanlines')
            self._load_scanlines()

        # must never happen
        if self._scanlines is None:
            return []
        return self._scanlines

    @scanlines.setter
    def scanlines(self, value: List[Scanline]) -> None:
        self._scanlines = value

    def show(self) -> None:
        from PIL import Image as PilImage

        # raw_data = self.to_bytes()

        color_type = self.header.color_type
        pixel_len = self.header.pixel_len
        pil_pixel_type = 'RGB'

        if color_type == 0:  # Greyscale
            pil_pixel_type = 'L'  # 1
        elif color_type == 2:  # RGB
            pil_pixel_type = 'RGB'  # 3
        elif color_type == 3:  # Palette
            pil_pixel_type = 'RGB'  # 3
            pixel_len = 3  # pixel len in output image must is 3
        elif color_type == 4:  # Greyscale + alpha
            pil_pixel_type = 'LA'  # 2
        elif color_type == 6:  # RGB + Alpha
            pil_pixel_type = 'RGBA'  # 4

        pil_img = PilImage.new(
            pil_pixel_type, (self.header.width + 1, len(self.scanlines)))
        data: List[Union[Tuple[int, int, int, int], int]] = []
        for sc in self.scanlines:
            filter_pixel = (sc.filter, sc.filter, sc.filter, 1)
            if pixel_len == 1:
                data.append(filter_pixel[0])
                raw_sc = list(map(lambda x: x[0], self._get_pixels(sc.data)))
                if len(raw_sc) < self.header.width:
                    raw_sc += [0]*(self.header.width-len(raw_sc))
                data += raw_sc

            else:
                data.append(filter_pixel)
                raw_sc = self._get_pixels(sc.data)
                if len(raw_sc) < self.header.width:
                    raw_sc += [(0, 0, 0, 1)]*(self.header.width-len(raw_sc))
                data += raw_sc

        logging.info('display image of size %s', pil_img.size)

        pil_img.putdata(data)
        pil_img.show()

    def to_bytes(self) -> bytes:
        data = bytearray()
        recon = None
        for scanline in self.scanlines:
            try:
                raw = apply_filter(
                    self.header, scanline.filter, scanline.data, recon)
            except IndexError:
                logging.exception('error on scanline %r', scanline.data)
                raise
            recon = scanline.data
            data.append(scanline.filter)
            data += raw
        return data

    def _get_pixels(self, row):
        pixels = []
        px_len = self.header.pixel_len

        if self.palette:
            pixels = [self.palette[i] for i in row]
        else:
            px = []
            bit_depth = self.header.bit_depth
            for val in BitArray(row, bit_depth):
                if bit_depth != 8:
                    # shrink value between 0 and 255
                    val = val * (2**bit_depth - 1)
                px.append(val)
                if len(px) == px_len:
                    pixels.append(tuple(px))
                    px = []
        return pixels

    def _save_pixels(self, row_data) -> bytes:
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
                    # print("Missing pixel %s in palette" % px)
                    # px_ko += 1
                    row_ret += px[0].to_bytes(1, 'big')
            # print("ok:%d ko:%d sum:%d" % (px_ok, px_ko, px_ok+px_ko))

        else:
            for px in row_data.pixels:
                row_ret += px.to_bytes()
        return row_ret
