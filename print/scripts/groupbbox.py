import sys, glob, os, pymupdf, numpy as np
from pdfops import top_groups
PT = 72/25.4

def page_stream(doc, p):
    return b'\n'.join(doc.xref_stream(x) for x in p.get_contents())

def group_boxes(path, pno, dpi=40):
    base = pymupdf.open(path); s = page_stream(base, base[pno])
    gs, _ = top_groups(s)
    out = []
    for k, (a, b) in enumerate(gs):
        d = pymupdf.open(path); p = d[pno]; xs = p.get_contents()
        d.update_stream(xs[0], s[a:b])
        for x in xs[1:]: d.update_stream(x, b' ')
        pix = p.get_pixmap(dpi=dpi, alpha=True)
        al = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 3]
        ys, xs_ = np.where(al > 8)
        kk = dpi / 25.4
        box = (xs_.min()/kk, ys.min()/kk, (xs_.max()+1)/kk, (ys.max()+1)/kk) if len(ys) else None
        out.append((k, a, b, box, int((al > 8).sum())))
    return s, out

if __name__ == '__main__':
    import paths
    f = sorted(glob.glob(os.path.join(paths.DESIGNER, '%s*.pdf' % sys.argv[1])))[0]
    s, out = group_boxes(f, int(sys.argv[2]))
    for k, a, b, box, n in out:
        print('%3d %7d bytes  %s  ink px %d' % (k, b - a, ('x %.1f-%.1f y %.1f-%.1f' % (box[0], box[2], box[1], box[3])) if box else 'nothing visible', n))
