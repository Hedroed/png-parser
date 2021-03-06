from pngparser import PngParser
import sys


def remove_idats(png):

    header = png.get_header()
    img = png.get_image_data()

    height = header.height
    rows_count = len(img.scanlines)

    print(f"[!] Height: {height}, real size: {rows_count}")

    img.scanlines = img.scanlines[:height]  # remove data out of image bounds
    png.set_image_data(img)


if __name__ == "__main__":
    png = PngParser(sys.argv[1])

    remove_idats(png)

    png.save_file("out.png")
    print('[*] Done')
