"""Find the illustration: the run of top-level content groups drawn in the left body area."""
import glob, os, pymupdf, numpy as np
from pdfops import top_groups, tokens
from groupbbox import page_stream
PT = 72/25.4


def ink_box(path, pno, seg, dpi=40):
    d = pymupdf.open(path); p = d[pno]; xs = p.get_contents()
    d.update_stream(xs[0], seg)
    for x in xs[1:]:
        d.update_stream(x, b' ')
    pix = p.get_pixmap(dpi=dpi, alpha=True)
    al = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 3]
    ys, xs_ = np.where(al > 8)
    if not len(ys):
        return None
    k = dpi / 25.4
    return (xs_.min() / k, ys.min() / k, (xs_.max() + 1) / k, (ys.max() + 1) / k)


def hero_run(path, pno):
    base = pymupdf.open(path)
    s = page_stream(base, base[pno])
    gs, loose = top_groups(s)
    info = []
    for k, (a, b) in enumerate(gs):
        seg = s[a:b]
        dos = sum(1 for kind, x, y in tokens(seg) if kind == 'op' and seg[x:y] == b'Do')
        paths = sum(1 for kind, x, y in tokens(seg) if kind == 'op' and seg[x:y] in (b'f', b'f*', b'B', b'B*', b'b', b'S', b's'))
        info.append((k, a, b, ink_box(path, pno, seg), dos, paths))
    def in_left(bx):
        return bx and bx[2] < 92 and bx[1] > 22.0 and bx[3] < 91 and (bx[2] - bx[0]) < 100
    # illustration groups: drawn in the left body, made of paths (not Do-only dot grids / images)
    cand = [i for i in info if in_left(i[3]) and i[5] > 0 and not (i[4] and i[5] == 0)]
    first, last = cand[0][0], cand[-1][0]
    run = info[first:last + 1]
    stray = [i[0] for i in run if i[3] and not in_left(i[3])]
    a, b = run[0][1], run[-1][2]
    loose_inside = [s[x:y] for x, y, w in loose if a < x < b]
    u = [i[3] for i in run if i[3]]
    box = (min(v[0] for v in u), min(v[1] for v in u), max(v[2] for v in u), max(v[3] for v in u))
    return dict(s=s, a=a, b=b, first=first, last=last, box=box, stray=stray, loose=loose_inside, ngroups=len(gs))


if __name__ == '__main__':
    import paths
    for f in sorted(glob.glob(os.path.join(paths.DESIGNER, '*.pdf'))):
        for pno in range(2):
            r = hero_run(f, pno)
            print('%-14s p%d  groups %d-%d of %d  box x %.1f-%.1f y %.1f-%.1f  stray-in-run %s  loose ops inside %s'
                  % (os.path.basename(f)[:14], pno + 1, r['first'], r['last'], r['ngroups'], r['box'][0], r['box'][2], r['box'][1], r['box'][3], r['stray'], r['loose'][:4]))
