"""Generate the served webfonts from the licensed originals.

Two things happen here.

Format: the supplied files are OTF and TTF (~960 KB for six faces), which
browsers fetch uncompressed. They are written as woff2 instead.

Subsetting: the full faces carry Cyrillic, Greek, Vietnamese and more, none of
which these pages use. Cutting them down to Latin takes the four faces a page
actually loads from 224 KB to 79 KB — by a wide margin the biggest saving
available on these pages.

The subset keeps Basic Latin, Latin-1 Supplement and Latin Extended-A, so
Western and Central European copy still sets correctly, along with general
punctuation, currency symbols and the ﬁ/ﬂ ligatures. A character outside that
range falls back to the next font in the stack rather than showing a blank box,
and `unicode-range` in the @font-face rules tells the browser not to fetch the
file for such text at all.

If the pages ever need a non-Latin script, widen UNICODES below (or drop the
--unicodes argument to ship the full faces) and re-run.

Usage:

    pip install fonttools brotli
    python scripts/build-fonts.py
"""

import glob
import os
import sys

from fontTools import subset

SRC = 'fonts-src'
DST = os.path.join('public', 'fonts')

UNICODES = [
    'U+0000-00FF',    # Basic Latin + Latin-1 Supplement
    'U+0100-017F',    # Latin Extended-A
    'U+2000-206F',    # general punctuation — dashes, quotes, bullet, ellipsis
    'U+20A0-20BF',    # currency symbols, for the £ fees
    'U+2122',         # ™
    'U+2212',         # minus
    'U+FB01-FB02',    # ﬁ ﬂ ligatures
]

# Only the features the pages need. Dropping the rest saves a little more and
# avoids shipping layout tables for scripts that are no longer present.
FEATURES = 'kern,liga,ccmp,locl'


def main():
    if not os.path.isdir(SRC):
        sys.exit('%s not found — the licensed originals live there.' % SRC)
    os.makedirs(DST, exist_ok=True)

    sources = sorted(glob.glob(os.path.join(SRC, '*.otf'))
                     + glob.glob(os.path.join(SRC, '*.ttf')))
    if not sources:
        sys.exit('no OTF/TTF found in %s' % SRC)

    before = after = 0
    for src in sources:
        name = os.path.splitext(os.path.basename(src))[0]
        out = os.path.join(DST, name + '.woff2')
        subset.main([
            src,
            '--unicodes=' + ','.join(UNICODES),
            '--layout-features=' + FEATURES,
            '--flavor=woff2',
            '--output-file=' + out,
        ])
        a, b = os.path.getsize(src), os.path.getsize(out)
        before += a
        after += b
        print('%-28s %7.1f KB -> %6.1f KB' % (name, a / 1024, b / 1024))

    print('\n%d faces: %.0f KB of originals -> %.0f KB served'
          % (len(sources), before / 1024, after / 1024))


if __name__ == '__main__':
    main()
