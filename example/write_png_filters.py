from pngparser import PngParser
import sys


def hideData(png, data: bytes):

    img = png.get_image_data()

    rows_count = len(img.rows)

    # 2 bytes by line
    max_data_to_hide = 2 * rows_count
    current = len(data) * 8
    if current > max_data_to_hide:
        raise Exception("Too Many Data: Too many data to hide, max %db, current %db" % (
            max_data_to_hide, current))

    data_bin = ''.join("{:08b}".format(i) for i in data)
    splitted_data_bin = [data_bin[i:i+2] for i in range(0, len(data_bin), 2)]

    for y, r in enumerate(img.rows):
        if y < len(splitted_data_bin):
            new_filter_id = int(splitted_data_bin[y], 2)
            r.update_filter(new_filter_id)
        elif y == len(splitted_data_bin):
            r.update_filter(4)

    png.set_image_data(img)


if __name__ == "__main__":
    png = PngParser(sys.argv[1])

    data = b"luke i am your father"
    hideData(png, data)

    png.save_file("out.png")
    print('[*] Done')
