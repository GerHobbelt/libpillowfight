import unittest

import PIL.Image
import PIL.ImageDraw

import pillowfight


class TestScanBorder(unittest.TestCase):
    def test_scan_border_a(self):
        in_img = PIL.Image.open("tests/data/brother_mfc7360.jpeg")
        frame = pillowfight.find_scan_border(in_img)
        self.assertEqual(frame, (56, 8, 1637, 2275))

    def test_scan_border_b(self):
        in_img = PIL.Image.open("tests/data/epson_xp425.jpeg")
        frame = pillowfight.find_scan_border(in_img)
        self.assertEqual(frame, (4, 5, 2484, 3498))

    def test_scan_border_c(self):
        in_img = PIL.Image.open("tests/data/brother_ds620.jpeg")
        frame = pillowfight.find_scan_border(in_img)
        self.assertEqual(frame, (3, 3, 2507, 3527))
