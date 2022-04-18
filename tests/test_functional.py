import unittest
from io import BytesIO
import tempfile

import pngparser

SIMPLE_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x03\x00\x00\x00\x01\x08\x02\x00\x00\x00\x94\x82\x83\xe3\x00\x00\x00\x15'
    b'IDAT\x08\x1d\x01\n\x00\xf5\xff\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x0e\xfb\x02\xfe\xe92a\xe5\x00\x00\x00\x00IEND\xaeB`\x82'
)

class TestCaseFunctional(unittest.TestCase):

    def test_loading_png(self):
        png = pngparser.PngParser(BytesIO(SIMPLE_PNG))

        self.assertEqual(len(png.get_all()), 3, png.get_all())

    def test_saving_recreate_same_file(self):
        png = pngparser.PngParser(BytesIO(SIMPLE_PNG))

        with tempfile.NamedTemporaryFile() as tmp_file:
            png.save_file(tmp_file.name)

            tmp_file.seek(0)
            content = tmp_file.read()

        self.assertEqual(content, SIMPLE_PNG)
