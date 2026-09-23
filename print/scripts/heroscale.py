"""Scale a card's illustration in place by wrapping its content-stream run in a cm.

The run is found by herorun.hero_run. Loose graphics-state operators inside the
run (colour, transparency, line width) would stop at the wrapper's Q, so they are
repeated after it: everything drawn later sees exactly the state it saw before.
"""
import pymupdf
from pdfops import tokens
from herorun import hero_run

PT = 72.0 / 25.4
STATE = {b'rg', b'RG', b'g', b'G', b'k', b'K', b'gs', b'w', b'J', b'j', b'd', b'cs', b'CS',
         b'sc', b'scn', b'SC', b'SCN', b'ri', b'i', b'M'}


def loose_state_ops(seg):
    """Depth-0 state operators (with operands) inside a run, in order."""
    out, depth, operand_start = [], 0, 0
    for kind, a, b in tokens(seg):
        if kind != 'op':
            continue
        w = seg[a:b]
        if w == b'q':
            depth += 1
        elif w == b'Q':
            depth -= 1
        elif depth == 0 and w in STATE:
            out.append(seg[operand_start:b].strip())
        operand_start = b
    return out


def scale_hero(path, doc, pno, factor, anchor_mm):
    """Scale the illustration on doc[pno] by factor about anchor (x, y in mm from top-left).
    Returns (old_box, new_box) in mm."""
    r = hero_run(path, pno)
    s, a, b = r['s'], r['a'], r['b']
    page = doc[pno]
    H = page.rect.height
    ax, ay = anchor_mm[0] * PT, H - anchor_mm[1] * PT
    cm = b'q %.6f 0 0 %.6f %.4f %.4f cm\n' % (factor, factor, ax * (1 - factor), ay * (1 - factor))
    restore = b'\n'.join(loose_state_ops(s[a:b]))
    new = s[:a] + cm + s[a:b] + b'\nQ\n' + restore + b'\n' + s[b:]
    xs = page.get_contents()
    doc.update_stream(xs[0], new)
    for x in xs[1:]:
        doc.update_stream(x, b' ')
    x0, y0, x1, y1 = r['box']
    f = factor
    nb = (anchor_mm[0] + (x0 - anchor_mm[0]) * f, anchor_mm[1] + (y0 - anchor_mm[1]) * f,
          anchor_mm[0] + (x1 - anchor_mm[0]) * f, anchor_mm[1] + (y1 - anchor_mm[1]) * f)
    return r['box'], nb
