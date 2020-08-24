import tempfile
import unittest

import PIL.Image

import pillowfight


class TestSWT(unittest.TestCase):
    def test_swt(self):
        with tempfile.NamedTemporaryFile(suffix='.png') as tmpfile:
            in_img = PIL.Image.open("tests/data/crappy_background.png")
            out_img = pillowfight.swt(
                in_img, output_type=pillowfight.SWT_OUTPUT_ORIGINAL_BOXES
            )
            in_img.close()

            # beware of JPG compression
            self.assertEqual(out_img.mode, "RGB")
            out_img.save(tmpfile.name)
            out_img.close()
            out_img = PIL.Image.open(tmpfile.name)

        expected_img = PIL.Image.open(
            "tests/data/crappy_background_swt.png"
        )
        self.assertEqual(out_img.tobytes(), expected_img.tobytes())
        expected_img.close()

    def test_swt2(self):
        with tempfile.NamedTemporaryFile(suffix='.png') as tmpfile:
            in_img = PIL.Image.open("tests/data/black_border_problem.png")
            out_img = pillowfight.swt(
                in_img, output_type=pillowfight.SWT_OUTPUT_ORIGINAL_BOXES
            )
            in_img.close()

            # beware of JPG compression
            self.assertEqual(out_img.mode, "RGB")
            out_img.save(tmpfile.name)
            out_img.close()
            out_img = PIL.Image.open(tmpfile.name)

        expected_img = PIL.Image.open(
            "tests/data/black_border_problem_swt.png"
        )
        self.assertEqual(out_img.tobytes(), expected_img.tobytes())
        expected_img.close()
