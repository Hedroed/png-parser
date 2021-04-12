from pngparser import PngParser, ChunkTypes

import sys


def extractData(png):

    header = png.get_by_type(ChunkTypes.IHDR)[0]
    print(header.data, file=sys.stderr)

    data = bytes(png.get_image_data())
    return data


if __name__ == "__main__":
    png = PngParser(sys.argv[1])
    # png = PngParser("example/example.png")

    data = extractData(png)
    print(len(data))

    with open(sys.argv[2], 'wb') as f:
        f.write(data)
