#!/usr/bin/env python3

import multiprocessing.pool
import os
import sys

import PIL.Image
import PIL.ImageDraw

import pillowfight


SCAN_URL_FMT = "https://openpaper.work/scannerdb/report/{id}/scanned.png"


count = 0


def _find_scan_borders(img_in):
    img_in = img_in.copy()
    frame = pillowfight.find_scan_border(img_in)

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


def find_scan_borders(report_id, img_in, total):
    global count

    progress = int(20 * (count / total))
    progress = ("=" * progress) + (" " * (20 - progress))
    sys.stdout.write(f"\r[{progress}] {count}/{total}")
    sys.stdout.flush()

    img_in = img_in.convert("RGB")
    img_out = _find_scan_borders(img_in)

    count += 1
    return (report_id, img_in, img_out)


def main():
    global count

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    os.makedirs(out_dir, exist_ok=True)

    pool = multiprocessing.pool.ThreadPool(
        multiprocessing.cpu_count()
    )

    print("Loading ...")
    all_files = list(os.listdir(in_dir))

    for x in range(0, len(all_files), 64):
        imgs = []

        for scan in all_files[x:x + 64]:
            if not scan.startswith("in_"):
                continue
            report_id = int(scan[len("in_"):-len(".jpeg")])

            img_in = PIL.Image.open(os.path.join(in_dir, scan))
            imgs.append((report_id, img_in))

        print("Processing ...")
        imgs = pool.map(
            lambda args: find_scan_borders(args[0], args[1], len(all_files)),
            imgs
        )

        print()
        print("Writing ...")
        for (report_id, img_in, img_out) in imgs:
            assembly = [img_in, img_out]
            (widths, heights) = zip(*(i.size for i in assembly))
            total_width = sum(widths)
            max_height = max(heights)

            img = PIL.Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for i in assembly:
                img.paste(i, (x_offset, 0))
                x_offset += i.size[0]
            img.save(os.path.join(out_dir, f"out_{report_id}.jpeg"))

    print("Done")


if __name__ == "__main__":
    main()
