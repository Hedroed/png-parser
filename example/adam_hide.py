from pngparser import PngParser, ImageData, TYPE_IHDR, TYPE_IDAT, ChunkRaw

import sys
import math
import zlib


_adam7 = ((0, 0, 8, 8),
          (4, 0, 8, 8),
          (0, 4, 4, 8),
          (2, 0, 4, 4),
          (0, 2, 2, 4),
          (1, 0, 2, 2),
          (0, 1, 1, 2))


def deinterlace(header, raw: bytearray):
    """
    Read raw pixel data, undo filters, deinterlace, and flatten.
    Return in flat row flat pixel format.
    """

    # Make a result array, and make it big enough.  Interleaving
    # writes to the output array randomly (well, not quite), so the
    # entire output array must be in memory.
    source_offset = 0

    cnt = 0

    for xstart, ystart, xstep, ystep in _adam7:
        if xstart >= header.width:
            continue
        # The previous (reconstructed) scanline.  None at the
        # beginning of a pass to indicate that there is no previous
        # line.
        recon = None
        # Pixels per row (reduced pass image)
        ppr = int(math.ceil((header.width-xstart)/float(xstep)))
        # Row size in bytes for this pass.
        row_size = int(math.ceil(header.pixel_len * ppr))
        for y in range(ystart, header.height, ystep):
            filter_type = raw[source_offset]
            if source_offset == 0:
                raw[source_offset] = 0
            else:
                raw[source_offset] = 4
            source_offset += 1

            print(f"[{cnt}] Read adam7 filter {filter_type!r} at {source_offset}")
            cnt += 1

            # scanline = raw[source_offset:source_offset+row_size]
            source_offset += row_size

    return raw


def extend_data(png):

    header = png.get_by_type(TYPE_IHDR)[0]

    img_data = png.get_image_data()

    # line_width = header.width * header.pixel_len + 1
    # img_data.scanlines.append(b'\x00' * line_width)
    # img_data = ImageData(header, img_data.scanlines)

    data = img_data.to_bytes()

    print(f"Raw data is {len(data)} length")

    res = deinterlace(header, bytearray(data))

    compressed_data = zlib.compress(res)

    new_idat = ChunkRaw(TYPE_IDAT, compressed_data)
    new_inserted = False
    new_chunks = []
    for chunk in png.chunks:
        if chunk.type == TYPE_IDAT:
            if not new_inserted:
                new_inserted = True
                new_chunks.append(new_idat)
        else:
            new_chunks.append(chunk)

    png.chunks = new_chunks

    header.interlace_method = 1  # force header interlace bit


if __name__ == "__main__":
    png = PngParser(sys.argv[1])

    extend_data(png)
    png.save_file("out.png")
