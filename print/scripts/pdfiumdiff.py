"""Render original and built cards with pdfium (Chrome/Edge engine) and report changes
outside the areas we intentionally edit."""
import glob, os, sys, numpy as np, pypdfium2 as pdfium
import paths
D = paths.DESIGNER
B = sys.argv[1] if len(sys.argv) > 1 else paths.CARDS
DPI = 100; k = DPI / 25.4
def render(path, pno):
    return np.asarray(pdfium.PdfDocument(path)[pno].render(scale=DPI/72).to_pil().convert('RGB')).astype(int)
for f in sorted(glob.glob(os.path.join(D, '*.pdf'))):
    stem = os.path.basename(f)[:12]
    bf = sorted(glob.glob(os.path.join(B, os.path.basename(f)[:20] + '*.pdf')))[0]
    for pno in range(2):
        a, b = render(f, pno), render(bf, pno)
        diff = np.abs(a - b).max(axis=2) > 40
        # intentional edit zones (mm): right column + QR, header right (URL/logo), footer email, left illustration area on Visit
        mask = np.zeros_like(diff)
        def z(x0, y0, x1, y1): mask[int(y0*k):int(y1*k), int(x0*k):int(x1*k)] = True
        z(62, 22.4, 148, 90.5)      # text column, label, QR
        z(95, 0, 148, 22.4)         # URL + LC logo
        z(95, 91, 148, 105)         # footer right (email)
        if 'Friends' in f and pno == 0: z(0, 0, 148, 22.4)       # header replaced on purpose
        if ('English' in f or 'Portuguese' in f) and pno == 1: z(0, 22.4, 75, 90.5)   # Visit: books + address
        out = diff & ~mask
        n = int(out.sum())
        if n:
            ys, xs = np.where(out)
            print('%-12s side %d: %6d unexpected changed px, x %.0f-%.0f y %.0f-%.0f mm' % (stem, pno+1, n, xs.min()/k, xs.max()/k, ys.min()/k, ys.max()/k))
        else:
            print('%-12s side %d: no unexpected changes' % (stem, pno+1))
