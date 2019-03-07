from pngparser import PngParser, ImageData, ChunkTypes

import sys

def replaceData(png, data):

        header_chunk = png.get_by_type(ChunkTypes.IHDR)[0]
        header = header_chunk.data

        data_length = len(data)
        line_width = header.width * header.pixel_len + 1
        scanlines = [data[i:i + line_width] for i in
                        range(0, data_length, line_width)]

        palette = None
        # If palette
        # if header.use_palette():
        #     palette_chunk = next(c for c in self.chunks if c.type == ChunkTypes.PLTE)
        #     palette = palette_chunk.data

        img = ImageData(header, scanlines, palette=palette)
        png.set_image_data(img)


if __name__ == "__main__":
    png = PngParser(sys.argv[1])

    with open(sys.argv[2], 'rb') as f:
        data = f.read()
        replaceData(png, data)
        png.save_file("out.png")
