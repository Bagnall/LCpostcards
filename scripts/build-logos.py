"""Generate the web-sized Cambridge wordmarks.

The supplied logos are ~2740px-wide PNGs of about 130 KB each. The header
renders them 56px tall, so they are resized to 2x that and written as WebP.
Both variants are needed: the cards use the reversed wordmark on dark bands and
the positive one on pale, and the .theme-* blocks in src/styles/main.css switch
between them per page.

Sources live in logos-src/, outside the served directory, so the oversized
originals are not copied into every deploy.

Usage:

    pip install pillow
    python scripts/build-logos.py
"""

import os
import sys

from PIL import Image

SRC = 'logos-src'
DST = os.path.join('public', 'assets')

HEIGHT = 112          # 2x the 56px rendered height
QUALITY = 90

VARIANTS = {
    # output name          source
    'logo-white.webp': 'ucam_language_centre_h_white.png',
    'logo-dark.webp': 'ucam_language_centre_h_black.png',
}


def main():
    if not os.path.isdir(SRC):
        sys.exit('%s not found.' % SRC)
    for out, src in VARIANTS.items():
        path = os.path.join(SRC, src)
        im = Image.open(path).convert('RGBA')
        w = round(im.width * HEIGHT / im.height)
        im = im.resize((w, HEIGHT), Image.LANCZOS)
        dest = os.path.join(DST, out)
        im.save(dest, 'WEBP', quality=QUALITY, method=6)
        print('%-18s %sx%s  %5.1f KB  (from %5.1f KB)' % (
            out, w, HEIGHT, os.path.getsize(dest) / 1024,
            os.path.getsize(path) / 1024))


if __name__ == '__main__':
    main()
