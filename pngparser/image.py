from PIL import Image as PilImage

from .pixel import Pixel

class Image():
    def __init__(self, pixel_type, width, height):
        self.width = width
        self.height = height
        self.pixel_type = pixel_type

        self.data = [Pixel(pixel_type)] * (width * height)

    def putpixel(self, position, pixel: Pixel):
        assert type(pixel) == Pixel, "Must be type Pixel"

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
        pil_img = PilImage.new(self.pixel_type, (self.width, self.height))
        pil_img.putdata(map(bytes, self.data))
        pil_img.show()
