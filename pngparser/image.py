from PIL import Image as PilImage

from .pixel import Pixel


class Image():
    def __init__(self, pixel_type, width, height):
        self.width = width
        self.height = height
        self.pixel_type = pixel_type

        self.data = [Pixel(pixel_type)] * (width * height)

    def putpixel(self, position, pixel: Pixel):
        # if not isinstance(pixel, Pixel):
        #     raise Exception("Must be type Pixel")

        x, y = position
        if x < 0 or x > self.width:
            raise IndexError("x outside image")
        if y < 0 or y > self.height:
            raise IndexError("y outside image")

        pos = x + y * self.width
        self.data[pos] = pixel

    def getpixel(self, position):
        x, y = position
        if x < 0 or x > self.width:
            raise IndexError("x outside image")
        if y < 0 or y > self.height:
            raise IndexError("y outside image")

        pos = x + y * self.width
        return self.data[pos]

    def show(self):

        pil_pixel_type = "RGB"
        if self.pixel_type == 0:  # Greyscale
            pil_pixel_type = 'L'  # 1
        elif self.pixel_type == 2:  # RGB
            pil_pixel_type = 'RGB'  # 3
        elif self.pixel_type == 4:  # Greyscale + alpha
            pil_pixel_type = 'LA'  # 2
        elif self.pixel_type == 6:  # RGB + Alpha
            pil_pixel_type = 'RGBA'  # 4

        pil_img = PilImage.new(pil_pixel_type, (self.width, self.height))
        pil_img.putdata(list(map(lambda x: x.values, self.data)))
        pil_img.show()
