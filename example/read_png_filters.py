from pngparser import PngParser, ImageData, ChunkTypes

import sys

def extractData(png):

        header = png.get_by_type(ChunkTypes.IHDR)[0]
        print(header.data)

        img = png.get_image_data()

        data_bin = ""
        print("[*] filter ", end='')
        for r in img.rows:
            print('%s' % r.filter, end='')
            if r.filter >= 4:
                break
            d = r.filter % 4
            f = "{:02b}".format(d)
            data_bin += f
        print()

        data = b''.join(int(data_bin[i:i+8], 2).to_bytes(1, 'big')
                        for i in range(0, len(data_bin), 8))
        return data

if __name__ == "__main__":
    png = PngParser(sys.argv[1])
    # png = PngParser("example/example.png")

    data = extractData(png)

    print(data)
