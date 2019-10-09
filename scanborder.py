#!/usr/bin/env python3

import sys

import PIL.Image
import PIL.ImageDraw

import pillowfight


def find_scan_borders(img_in, img_out):
    img_in = PIL.Image.open(img_in)

    img = img_in.copy()
    # img = pillowfight.unpaper_blackfilter(img)
    # img = pillowfight.unpaper_noisefilter(img)
    # img = pillowfight.unpaper_blurfilter(img)
    # img = pillowfight.unpaper_masks(img)

    frame = pillowfight.find_scan_borders(img)

    draw = PIL.ImageDraw.Draw(img_in)
    draw.rectangle(
        ((0, 0), (frame[0], img_in.size[1])),
        fill=(0xc4, 0x00, 0xff)
    )
    draw.rectangle(
        ((0, 0), (img_in.size[0], frame[1])),
        fill=(0xc4, 0x00, 0xff)
    )
    draw.rectangle(
        ((frame[2], 0), (img_in.size[0], img_in.size[1])),
        fill=(0xc4, 0x00, 0xff)
    )
    draw.rectangle(
        ((0, frame[3]), (img_in.size[0], img_in.size[1])),
        fill=(0xc4, 0x00, 0xff)
    )
    img_in.save(img_out)


def main():
    find_scan_borders(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
