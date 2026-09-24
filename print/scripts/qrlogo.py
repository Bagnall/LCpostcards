"""Vector QR (full URL, level H) with the LC logo in a cleared centre square.

The clear zone is a whole number of modules, so no module is part-covered; the
logo sits inside it with PAD modules of white on every side.
"""
import os
import pymupdf
import segno

import paths
LOGO = os.path.join(paths.LOGOS, 'LC_logo_Black_LightMode_SVG.svg')
PT = 72.0 / 25.4
CLEAR = 15      # modules cleared in the centre (odd, so it centres exactly)
PAD = 2.0       # modules of white between the logo and the nearest module

LONG = {s: 'https://duns.langcen.cam.ac.uk/lcpostcard/%s.html' % p for s, p in {
    'eng-conv': 'english-conversation-hours',
    'lc-visit': 'visit-our-study-centre',
    'inter-conv': 'intermediate-conversation-hours',
    'adv-conv': 'advanced-conversation-hours',
    'lc-friends': 'friends-without-frontiers',
    'conv-exch': 'conversation-exchange',
    'lc-adv': 'language-advising',
    'lc-abroad': 'study-abroad',
    'port-conv': 'portuguese-conversation-hours',
}.items()}

_logo = None


def logo_doc():
    global _logo
    if _logo is None:
        from svglogo import logo_pdf
        _logo = logo_pdf(LOGO)          # honours the SVG's own colour classes
    return _logo


def draw_qr(page, url, x0_mm, y0_mm, size_mm, clear=CLEAR, pad=PAD):
    """Draw the code at (x0, y0) mm, size_mm square. Returns info dict."""
    q = segno.make(url, error='H', version=8, boost_error=False)  # same grid (and logo size) on every card
    m = [[1 if b else 0 for b in row] for row in q.matrix]
    n = len(m)
    mod = size_mm / n
    lo = (n - clear) // 2
    hi = lo + clear
    page.draw_rect(pymupdf.Rect(x0_mm * PT, y0_mm * PT, (x0_mm + size_mm) * PT,
                                (y0_mm + size_mm) * PT), color=None, fill=(1, 1, 1), overlay=True)
    dark = cleared = 0
    for r in range(n):
        for c in range(n):
            if not m[r][c]:
                continue
            if lo <= r < hi and lo <= c < hi:
                cleared += 1
                continue
            dark += 1
            x, y = (x0_mm + c * mod) * PT, (y0_mm + r * mod) * PT
            page.draw_rect(pymupdf.Rect(x, y, x + mod * PT + 0.08, y + mod * PT + 0.08),
                           color=None, fill=(0, 0, 0, 1), overlay=True)   # 100% K modules
    # logo box: the clear square less the padding, logo fitted by height
    inner = (clear - 2 * pad) * mod
    lr = logo_doc()[0].rect
    lh = inner
    lw = inner * lr.width / lr.height
    cx = x0_mm + (lo + clear / 2.0) * mod
    cy = y0_mm + (lo + clear / 2.0) * mod
    box = pymupdf.Rect((cx - lw / 2) * PT, (cy - lh / 2) * PT, (cx + lw / 2) * PT, (cy + lh / 2) * PT)
    page.show_pdf_page(box, logo_doc(), 0, overlay=True)
    return dict(version=q.version, n=n, mod=mod, clear_mm=clear * mod,
                logo_w=lw, logo_h=lh, area=clear * clear / float(n * n),
                cleared_dark=cleared)
