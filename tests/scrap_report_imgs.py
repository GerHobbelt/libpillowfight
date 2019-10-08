#!/usr/bin/env python3

import os
import sys
import urllib.error
import urllib.request

import PIL
import PIL.Image


SCAN_URL_FMT = "https://openpaper.work/scannerdb/report/{id}/scanned.png"


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

        img = PIL.Image.open(scan)
        print(f"Image size: {img.size}")
        if img.size[0] < 256 or img.size[1] < 256:
            print("Too small")
            continue

        img.save(os.path.join(out_dir, f"in_{report_id}.jpeg"))
        print("Done")


if __name__ == "__main__":
    main()
