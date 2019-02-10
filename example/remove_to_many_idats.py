from pngparser import PngParser
import sys

def removeIdats(png):

        header = png.get_header()
        img = png.get_image_data()

        height = header.height
        rows_count = len(img.rows)

        print("[!] Height: %d, real size: %d" % (height, rows_count))

        img.rows = img.rows[:height]
        png.set_image_data(img)

if __name__ == "__main__":
    png = PngParser(sys.argv[1])

    removeIdats(png)

    png.save_file("example/tmp.png")
    print('[*] Done')
