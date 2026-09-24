"""Export each card's illustration from the designer's card PDFs, for the landing pages.

The illustration is found as its own run of content groups (herorun.hero_run), drawn
alone on a page cropped to its bounds, and written as SVG. Everything else on the
card (dot grid, text, header, QR) is left out.

    python print/scripts/export_illustrations.py [outdir]
"""
import os, sys
import pymupdf
import paths
from herorun import hero_run

PT = 72 / 25.4
SIDES = {  # (designer file prefix, page) -> landing page slug
    ('English', 0): 'english-conversation-hours', ('English', 1): 'visit-our-study-centre',
    ('French', 0): 'intermediate-conversation-hours', ('French', 1): 'advanced-conversation-hours',
    ('Friends', 0): 'friends-without-frontiers', ('Friends', 1): 'conversation-exchange',
    ('Language', 0): 'language-advising', ('Language', 1): 'study-abroad',
    ('Portuguese', 0): 'portuguese-conversation-hours',
}


def export(src_path, pno, out_svg, pad_mm=0.5):
    r = hero_run(src_path, pno)
    doc = pymupdf.open(src_path)
    page = doc[pno]
    xs = page.get_contents()
    doc.update_stream(xs[0], r['s'][r['a']:r['b']])     # just the illustration's groups
    for x in xs[1:]:
        doc.update_stream(x, b' ')
    x0, y0, x1, y1 = r['box']
    clip = pymupdf.Rect((x0 - pad_mm) * PT, (y0 - pad_mm) * PT, (x1 + pad_mm) * PT, (y1 + pad_mm) * PT)
    page.set_cropbox(clip)
    # scale to ~900 units wide, like the designer's own SVGs, so the site's SVGO settings
    # (coordinates rounded to 0.1 unit) stay far below a pixel
    z = 900.0 / clip.width
    svg = page.get_svg_image(matrix=pymupdf.Matrix(z, z), text_as_path=True)
    with open(out_svg, 'w', encoding='utf-8') as f:
        f.write(svg)
    return r['box'], len(svg)


if __name__ == '__main__':
    import glob
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(paths.BUILD, 'illustrations')
    os.makedirs(out, exist_ok=True)
    for (pre, pno), slug in SIDES.items():
        src = glob.glob(os.path.join(paths.DESIGNER, pre + '*.pdf'))[0]
        box, n = export(src, pno, os.path.join(out, slug + '.svg'))
        print('%-34s %.1f x %.1f mm  %6.0f KB' % (slug, box[2] - box[0], box[3] - box[1], n / 1024))
