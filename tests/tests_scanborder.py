import unittest

import PIL.Image
import PIL.ImageDraw

import pillowfight


class TestScanBorder(unittest.TestCase):
    def test_scan_border_a(self):
        in_img = PIL.Image.open("tests/data/brother_mfc7360.jpeg")
        frame = pillowfight.find_scan_border(in_img)
        self.assertEqual(frame, (8, 37, 1637, 2195))

    def test_scan_border_b(self):
        in_img = PIL.Image.open("tests/data/epson_xp425.jpeg")
        frame = pillowfight.find_scan_border(in_img)
        self.assertEqual(frame, (11, 4, 2541, 3503))

    def test_scan_border_c(self):
        in_img = PIL.Image.open("tests/data/brother_ds620.jpeg")
        frame = pillowfight.find_scan_border(in_img)
        self.assertEqual(frame, (3, 3, 2507, 3527))
