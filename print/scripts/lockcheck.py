import glob, numpy as np, pypdfium2 as pdfium
def lock(path, pno, ox, oy):
    img = pdfium.PdfDocument(path)[pno].render(scale=300/72).to_pil().convert('RGB'); k = 300/25.4
    a = np.asarray(img.crop((int((13+ox)*k), int((6.5+oy)*k), int((56+ox)*k), int((14+oy)*k)))).astype(int)
    crest = np.asarray(img.crop((int((7+ox)*k), int((7+oy)*k), int((12.5+ox)*k), int((13+oy)*k)))).astype(int)
    bg = np.median(a.reshape(-1, 3), axis=0); L = a[np.abs(a - bg).sum(axis=2) > 120]
    return np.median(L, axis=0), crest.reshape(-1, 3).mean(axis=0)
import os, paths
O = paths.DESIGNER
orig = [(f, p) for f in sorted(glob.glob(os.path.join(O, '*.pdf'))) for p in (0, 1)]
PR = os.path.join(paths.PRINT_READY, 'ALL-CARDS_A6_%s_QR20_print.pdf' % paths.VERSION)
RV = paths.REVIEW
bad = 0
for i, (f, p) in enumerate(orig):
    src = (glob.glob(os.path.join(O, 'FrenchGerman*.pdf'))[0], 0) if i == 4 else (f, p)
    o = lock(src[0], src[1], 0, 0)
    for lab, path, pg, ox, oy in (('print', PR, i, 9, 9), ('review', RV, i + 1, 31, 40)):
        r = lock(path, pg, ox, oy)
        dl, dc = np.abs(r[0] - o[0]).max(), np.abs(r[1] - o[1]).max()
        if dl > 25 or dc > 12:
            bad += 1; print('  side %d %s: lettering %s vs %s, crest %s vs %s' % (i+1, lab, r[0].astype(int), o[0].astype(int), r[1].astype(int), o[1].astype(int)))
print('lockup colour check in pdfium (Chrome/Edge): %s' % ('all 20 match the originals' if not bad else '%d mismatches' % bad))
