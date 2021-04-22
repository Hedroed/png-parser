from pngparser import PngParser, ImageData, TYPE_IHDR

import sys


def extractData(png):

    header = png.get_by_type(TYPE_IHDR)[0]

    img = png.get_image_data()

    data_bin = ""
    data = ""
    for sc in img.scanlines:
        data += str(sc.filter)

        # hidden challenge
        d = sc.filter % 4
        f = "{:02b}".format(d)
        data_bin += f

    print(f"[*] filter {data}\n")

    data = b''.join(int(data_bin[i:i+8], 2).to_bytes(1, 'big')
                    for i in range(0, len(data_bin), 8))
    print(data)


if __name__ == "__main__":
    png = PngParser(sys.argv[1])
    # png = PngParser("example/normal.png")
    extractData(png)
