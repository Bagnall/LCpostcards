"""Wrap trim-size cards for print with a mirrored 3mm bleed and outside crop marks.

The supplied artwork stops at the trim (its background raster overhangs by only
0.36mm). The bleed is synthesised by reflecting the artwork across each trim
edge: a raster of the card, padded symmetrically (corners reflect both ways),
is laid underneath, and the vector card is placed on top at exact size. At the
trim line the bleed is therefore continuous with the artwork - curves and
colour boundaries meet it without a step. Only the trimmed-off 3mm is
synthesised; the 148x105mm card is the vector artwork untouched.

Crop marks sit outside the bleed (offset 3mm from the trim, 5mm long) on a
larger sheet, so they never overlap artwork.
"""
import glob, io, math, os, sys
import numpy as np
import pymupdf
from PIL import Image

import paths
SRC = paths.CARDS
TAG = paths.VERSION
OUT = os.environ.get('BLEED_OUT', paths.PRINT_READY)
os.makedirs(OUT, exist_ok=True)

PT = 72.0 / 25.4
TRIM_W, TRIM_H = 148.0, 105.0
BLEED = 3.0
MARK_OFF, MARK_LEN, MARK_W = 3.0, 5.0, 0.25
SLUG = MARK_OFF + MARK_LEN + 1.0          # sheet margin around the trim
PAGE_W, PAGE_H = TRIM_W + 2 * SLUG, TRIM_H + 2 * SLUG
DPI = 450


def mm(v):
    return v * PT


def underlay(src, pno):
    """JPEG of the card with a mirrored border, and the rect it must occupy."""
    pix = src[pno].get_pixmap(dpi=DPI)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    px = 25.4 / DPI                           # mm per pixel; pixel i starts at i*px
    # the outermost pixels are only partly covered by the artwork and render pale;
    # reflecting them would put a hairline on the trim, so reflect from just inside
    e = 2
    full_w = int(round(TRIM_W / px))
    full_h = int(round(TRIM_H / px))
    a = a[e:full_h - e, e:full_w - e]
    b = int(math.ceil(BLEED / px)) + e + 2
    padded = np.pad(a, ((b, b), (b, b), (0, 0)), mode='symmetric')
    buf = io.BytesIO()
    Image.fromarray(padded).save(buf, 'JPEG', quality=93, subsampling=0)
    x0, y0 = SLUG + (e - b) * px, SLUG + (e - b) * px
    rect = pymupdf.Rect(mm(x0), mm(y0), mm(x0 + padded.shape[1] * px), mm(y0 + padded.shape[0] * px))
    return buf.getvalue(), rect


def make(src_path, out):
    src = pymupdf.open(src_path)
    for pno in range(src.page_count):
        page = out.new_page(width=mm(PAGE_W), height=mm(PAGE_H))
        trim = pymupdf.Rect(mm(SLUG), mm(SLUG), mm(SLUG + TRIM_W), mm(SLUG + TRIM_H))
        bleed = pymupdf.Rect(mm(SLUG - BLEED), mm(SLUG - BLEED),
                             mm(SLUG + TRIM_W + BLEED), mm(SLUG + TRIM_H + BLEED))
        data, rect = underlay(src, pno)
        page.draw_rect(page.rect, color=None, fill=(1, 1, 1))
        page.insert_image(rect, stream=data)
        # keep the underlay inside the bleed box: white out beyond it
        for r in (pymupdf.Rect(0, 0, page.rect.width, bleed.y0),
                  pymupdf.Rect(0, bleed.y1, page.rect.width, page.rect.height),
                  pymupdf.Rect(0, bleed.y0, bleed.x0, bleed.y1),
                  pymupdf.Rect(bleed.x1, bleed.y0, page.rect.width, bleed.y1)):
            page.draw_rect(r, color=None, fill=(1, 1, 1))
        page.show_pdf_page(trim, src, pno)
        page.set_trimbox(trim)
        page.set_bleedbox(bleed)
        k = dict(color=(0, 0, 0), width=MARK_W)
        for x in (trim.x0, trim.x1):
            for ya, yb in ((trim.y0 - mm(MARK_OFF), trim.y0 - mm(MARK_OFF + MARK_LEN)),
                           (trim.y1 + mm(MARK_OFF), trim.y1 + mm(MARK_OFF + MARK_LEN))):
                page.draw_line(pymupdf.Point(x, ya), pymupdf.Point(x, yb), **k)
        for y in (trim.y0, trim.y1):
            for xa, xb in ((trim.x0 - mm(MARK_OFF), trim.x0 - mm(MARK_OFF + MARK_LEN)),
                           (trim.x1 + mm(MARK_OFF), trim.x1 + mm(MARK_OFF + MARK_LEN))):
                page.draw_line(pymupdf.Point(xa, y), pymupdf.Point(xb, y), **k)


if __name__ == '__main__':
    combined = pymupdf.open()
    for f in sorted(glob.glob(os.path.join(SRC, '*.pdf'))):
        name = os.path.basename(f).replace('_A5_%s_QR20.pdf' % TAG, '_A6_%s_QR20_print.pdf' % TAG)
        one = pymupdf.open()
        make(f, one)
        one.save(os.path.join(OUT, name), garbage=4, deflate=True)
        combined.insert_pdf(one)
        print('  %-66s %d pages  %.1f MB' % (name, one.page_count, os.path.getsize(os.path.join(OUT, name)) / 1e6))
    cpath = os.path.join(OUT, 'ALL-CARDS_A6_%s_QR20_print.pdf' % TAG)
    combined.save(cpath, garbage=4, deflate=True)
    print('  %-66s %d pages  %.1f MB' % (os.path.basename(cpath), combined.page_count, os.path.getsize(cpath) / 1e6))
    p = pymupdf.open(cpath)[0]
    print('sheet %.1f x %.1f mm, trim %.1f x %.1f mm, bleed %.2f mm all round'
          % (p.mediabox.width / PT, p.mediabox.height / PT, p.trimbox.width / PT, p.trimbox.height / PT,
             (p.bleedbox.width - p.trimbox.width) / 2 / PT))
