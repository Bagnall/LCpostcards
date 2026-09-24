"""Render each page with MuPDF and pdfium and report where the two engines disagree."""
import sys, numpy as np, pymupdf, pypdfium2 as pdfium
pymupdf.TOOLS.set_aa_level(8)
path = sys.argv[1]; DPI = 100; k = DPI / 25.4
doc = pymupdf.open(path); pdf = pdfium.PdfDocument(path)
worst = 0
for i in range(doc.page_count):
    px = doc[i].get_pixmap(dpi=DPI)
    a = np.frombuffer(px.samples, np.uint8).reshape(px.height, px.width, px.n)[:, :, :3].astype(int)
    b = np.asarray(pdf[i].render(scale=DPI/72).to_pil().convert('RGB')).astype(int)
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    d = np.abs(a[:h, :w] - b[:h, :w]).max(axis=2)
    # ignore single-pixel anti-aliasing differences: need a 3x3 block of strong disagreement
    strong = d > 60
    core = strong[1:-1, 1:-1] & strong[:-2, 1:-1] & strong[2:, 1:-1] & strong[1:-1, :-2] & strong[1:-1, 2:]
    n = int(core.sum()); worst = max(worst, n)
    if n:
        ys, xs = np.where(core)
        print('  page %d: %d px disagree, x %.0f-%.0f y %.0f-%.0f mm' % (i+1, n, xs.min()/k, xs.max()/k, ys.min()/k, ys.max()/k))
    else:
        print('  page %d: engines agree' % (i+1))
