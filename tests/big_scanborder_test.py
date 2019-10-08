#!/usr/bin/env python3

import os
import sys
import urllib.error
import urllib.request

import PIL.Image
import PIL.ImageDraw

import pillowfight


SCAN_URL_FMT = "https://openpaper.work/scannerdb/report/{id}/scanned.png"


def scanborder(img_in):
    img_in = img_in.copy()

    img = img_in.copy()
    frame = pillowfight.find_scan_border(img)

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

    return img_in


def main():
    min_report_id = int(sys.argv[1])
    max_report_id = int(sys.argv[2])
    out_dir = sys.argv[3]

    os.makedirs(out_dir, exist_ok=True)

    for report_id in range(min_report_id, max_report_id + 1):
        print("")
        scan = SCAN_URL_FMT.format(id=report_id)
        print(f"Downloading {scan} ...")
        try:
            scan = urllib.request.urlopen(scan)
        except Exception as exc:
            print("Failed: {}".format(str(exc)))
            continue
        code = scan.getcode()
        print(f"Reply: {code}")
        if code != 200:
            continue

        img_in = PIL.Image.open(scan)
        print(f"Image size: {img_in.size}")
        if img_in.size[0] < 256 or img_in.size[1] < 256:
            print("Too small")
            continue

        try:
            img_out = scanborder(img_in)
        except Exception as exc:
            print(f"FAILED ({exc}")
            continue

        images = [img_in, img_out]
        (widths, heights) = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)

        img = PIL.Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for i in images:
            img.paste(i, (x_offset, 0))
            x_offset += i.size[0]
        img.save(os.path.join(out_dir, f"out_{report_id}.jpeg"))
        print("Done")


if __name__ == "__main__":
    main()
