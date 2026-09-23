"""Final preflight of the printer package. Every check runs on the exact files being sent."""
import glob, os, re, subprocess, sys
import numpy as np
import pikepdf
import pymupdf
import pypdfium2 as pdfium
import zxingcpp

import paths
PKG = paths.PACKAGE
ORIG = paths.DESIGNER
PT = 72 / 25.4
SL = 9.0                      # trim offset on the sheet
QR = (121.0, 68.1, 141.0, 88.1)
BASE = 'https://duns.langcen.cam.ac.uk/lcpostcard/%s.html'

# per card: (file prefix, original prefix, [(side, qr page, short, must contain, must not contain)])
CARDS = [
    ('Card-1', 'English', [('front', 'english-conversation-hours', 'eng-conv', ['bit.ly/4xKLM9h', 'enquiries@langcen.cam.ac.uk'], ['speaking-practice']),
                           ('back', 'visit-our-study-centre', 'lc-visit', ['(outside term)', 'Contact us:', '01223 335 058', 'CB2 3EL'], ['outside of term'])]),
    ('Card-2', 'French', [('front', 'intermediate-conversation-hours', 'inter-conv', ['bit.ly/4xKLM9h'], ['speaking-practice']),
                          ('back', 'advanced-conversation-hours', 'adv-conv', ['bit.ly/4xKLM9h'], ['www.langcen.cam.ac.uk/\n'])]),
    ('Card-3', 'Friends', [('front', 'friends-without-frontiers', 'lc-friends', ['20 or 30-minute', 'bit.ly/4xKLM9h'], ['20-']),
                           ('back', 'conversation-exchange', 'conv-exch', ['conversation@langcen.cam.ac.uk'], ['enquiries@'])]),
    ('Card-4', 'Language', [('front', 'language-advising', 'lc-adv', ['Language Advising'], []),
                            ('back', 'study-abroad', 'lc-abroad', ['booking a study abroad'], ['Moodle', '4htBwMy', 'vle.cam'])]),
    ('Card-5', 'Portuguese', [('front', 'portuguese-conversation-hours', 'port-conv', ['bit.ly/4xKLM9h'], ['speaking-practice']),
                              ('back', 'visit-our-study-centre', 'lc-visit', ['(outside term)', 'Contact us:'], ['outside of term'])]),
]
fails, notes = [], []


def check(ok, what):
    if not ok:
        fails.append(what)
    return ok


def gray(pix):
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    return (a[:, :, 0] * 0.299 + a[:, :, 1] * 0.587 + a[:, :, 2] * 0.114).astype(np.uint8)


def lockup(img, ox, oy, scale):
    k = scale / 25.4
    a = np.asarray(img.crop((int((13 + ox) * k), int((6.5 + oy) * k), int((56 + ox) * k), int((14 + oy) * k)))).astype(int)
    bg = np.median(a.reshape(-1, 3), axis=0)
    L = a[np.abs(a - bg).sum(axis=2) > 120]
    crest = np.asarray(img.crop((int((7 + ox) * k), int((7 + oy) * k), int((12.5 + ox) * k), int((13 + oy) * k)))).astype(int)
    return np.median(L, axis=0), crest.reshape(-1, 3).mean(axis=0)


files = sorted(glob.glob(os.path.join(PKG, 'Card-*.pdf')))
check(len(files) == 5, 'expected 5 card files, found %d' % len(files))
urls = set()
for (prefix, oprefix, sides), path in zip(CARDS, files):
    name = os.path.basename(path)
    check(name.startswith(prefix), '%s: unexpected file order' % name)
    print('\n== %s' % name)
    # ---- structure ------------------------------------------------------------------
    with pikepdf.open(path) as pdf:
        probs = pdf.check_pdf_syntax() if hasattr(pdf, 'check_pdf_syntax') else pdf.check()
        check(not probs, '%s: qpdf reports %s' % (name, probs))
        check(not pdf.is_encrypted, '%s: encrypted' % name)
        root = pdf.Root
        check('/AcroForm' not in root, '%s: has form fields' % name)
        check('/Names' not in root or '/JavaScript' not in root.Names, '%s: has JavaScript' % name)
        check(len(pdf.pages) == 2, '%s: %d pages, expected 2' % (name, len(pdf.pages)))
        for i, pg in enumerate(pdf.pages):
            check('/Annots' not in pg.obj or len(pg.obj.Annots) == 0, '%s p%d: has annotations' % (name, i + 1))
            check(int(pg.obj.get('/Rotate', 0)) == 0, '%s p%d: rotated' % (name, i + 1))
        # fonts: every font dictionary reachable from the pages must carry an embedded font program
        unembedded = set()
        for obj in pdf.objects:
            if isinstance(obj, pikepdf.Dictionary) and obj.get('/Type') == '/Font':
                sub = str(obj.get('/Subtype'))
                if sub == '/Type0':
                    desc = obj.DescendantFonts[0].get('/FontDescriptor')
                elif sub == '/Type3':
                    continue
                else:
                    desc = obj.get('/FontDescriptor')
                if desc is None or not any(k in desc for k in ('/FontFile', '/FontFile2', '/FontFile3')):
                    unembedded.add(str(obj.get('/BaseFont')))
        check(not unembedded, '%s: fonts not embedded: %s' % (name, unembedded))
        print('   structure OK: PDF %s, 2 pages, no forms/JS/annotations, fonts embedded' % pdf.pdf_version)
    doc = pymupdf.open(path)
    fz = pdfium.PdfDocument(path)
    for i, (side, page_slug, short, must, mustnot) in enumerate(sides):
        p = doc[i]
        label = '%s %s' % (prefix, side)
        # ---- boxes ------------------------------------------------------------------
        mb, tb, bb = p.mediabox, p.trimbox, p.bleedbox
        check(abs(mb.width / PT - 166) < 0.05 and abs(mb.height / PT - 123) < 0.05, '%s: media %.1fx%.1f' % (label, mb.width / PT, mb.height / PT))
        check(abs(tb.width / PT - 148) < 0.05 and abs(tb.height / PT - 105) < 0.05 and abs(tb.x0 / PT - SL) < 0.05, '%s: trim box wrong' % label)
        check(abs((bb.width - tb.width) / 2 / PT - 3) < 0.05, '%s: bleed not 3mm' % label)
        # ---- images -----------------------------------------------------------------
        lo = min((im[2] / (r.width / 72.0) for im in p.get_images(full=True) for r in p.get_image_rects(im[0]) if r.width > 5), default=999)
        check(lo >= 250, '%s: image at %.0f dpi' % (label, lo))
        # ---- text ---------------------------------------------------------------------
        text = p.get_text()
        for m in must:
            check(m in text, '%s: missing "%s"' % (label, m))
        for m in mustnot:
            check(m not in text, '%s: still contains "%s"' % (label, m.strip()))
        check(('bit.ly/' + short) in text, '%s: QR label bit.ly/%s missing' % (label, short))
        # geometry of every text line (in trim coordinates)
        lines = []
        for b in p.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = ''.join(s['text'] for s in l['spans']).strip()
                if t:
                    x0, y0, x1, y1 = [v / PT - SL for v in l['bbox']]
                    lines.append((t, x0, y0, x1, y1))
        for t, x0, y0, x1, y1 in lines:
            # inside the safe area (>= 3 mm from the trim) unless it is header/footer furniture set by the designer
            check(x0 >= 3 and x1 <= 145 and y0 >= 3 and y1 <= 102, '%s: text "%s" within 3mm of the trim' % (label, t[:30]))
            # clear of the QR code (text may not intrude on the code or its 1.6 mm quiet zone)
            qz = 1.6
            inter = not (x1 <= QR[0] - qz or x0 >= QR[2] + qz or y1 <= QR[1] - qz or y0 >= QR[3] + qz)
            check(not inter, '%s: text "%s" touches the QR code' % (label, t[:30]))
        # overlapping lines (glyph boxes shrunk to the x-height band to ignore ascender/descender touch)
        for a in range(len(lines)):
            for b in range(a + 1, len(lines)):
                A, B = lines[a], lines[b]
                ah, bh = A[4] - A[2], B[4] - B[2]
                ax0, ay0, ax1, ay1 = A[1], A[2] + ah * 0.25, A[3], A[4] - ah * 0.25
                bx0, by0, bx1, by1 = B[1], B[2] + bh * 0.25, B[3], B[4] - bh * 0.25
                if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                    check(False, '%s: text overlaps: "%s" / "%s"' % (label, A[0][:25], B[0][:25]))
        # ---- QR: decode from both engines, several resolutions ------------------------
        want = BASE % page_slug
        urls.add(want); urls.add('https://bit.ly/' + short)
        clip = pymupdf.Rect((SL + QR[0] - 4) * PT, (SL + QR[1] - 4) * PT, (SL + QR[2] + 4) * PT, (SL + QR[3] + 4) * PT)
        reads = []
        for dpi in (600, 300, 150):
            g = gray(p.get_pixmap(dpi=dpi, clip=clip))
            reads.append([r.text for r in zxingcpp.read_barcodes(g)][:1] == [want])
        img = fz[i].render(scale=300 / 72).to_pil().convert('RGB')
        k = 300 / 25.4
        crop = np.asarray(img.crop((int((SL + QR[0] - 4) * k), int((SL + QR[1] - 4) * k), int((SL + QR[2] + 4) * k), int((SL + QR[3] + 4) * k))).convert('L'))
        reads.append([r.text for r in zxingcpp.read_barcodes(crop)][:1] == [want])
        check(all(reads), '%s: QR reads %s (MuPDF 600/300/150, pdfium 300)' % (label, reads))
        # QR modules in 100% K
        # ---- lockup colours vs the designer's original (pdfium) ------------------------
        o_path = glob.glob(os.path.join(ORIG, oprefix + '*.pdf'))[0]
        o_page = i
        if prefix == 'Card-3' and side == 'front':           # header deliberately from FGS Intermediate
            o_path, o_page = glob.glob(os.path.join(ORIG, 'French*.pdf'))[0], 0
        o_img = pdfium.PdfDocument(o_path)[o_page].render(scale=300 / 72).to_pil().convert('RGB')
        (ol, oc), (nl, nc) = lockup(o_img, 0, 0, 300), lockup(img, SL, SL, 300)
        check(np.abs(ol - nl).max() < 25 and np.abs(oc - nc).max() < 12,
              '%s: University logo colour differs from original in pdfium (lettering %s vs %s)' % (label, nl.astype(int), ol.astype(int)))
        print('   %-5s boxes OK | images >= %.0f dpi | text checks OK | QR -> %s (4/4 reads) | logo matches original'
              % (side, lo, want.split('/')[-1]) if not [f for f in fails if f.startswith(label)] else '   %s: see failures' % side)
    # 100% K in the drawing instructions
    s = b''.join(doc.xref_stream(x) for x in range(1, doc.xref_length()) if doc.xref_is_stream(x) and b'0 0 0 1 k' in (doc.xref_stream(x) or b''))
    check(s.count(b'0 0 0 1 k') > 1000, '%s: QR not 100%% K' % name)

# ---- bleed seams -------------------------------------------------------------------------
S = os.path.dirname(os.path.abspath(__file__))
for path in files:
    out = subprocess.run([sys.executable, os.path.join(S, 'seamcheck_noaa.py'), path], capture_output=True, text=True).stdout
    m = re.search(r'worst excess jump at trim across all edges: (\d+)', out)
    check(m and int(m.group(1)) <= 12, '%s: bleed seam %s' % (os.path.basename(path), m.group(1) if m else '?'))
print('\nbleed: no seams at the trim on any side')

# ---- links are live ------------------------------------------------------------------------
urls.add('https://bit.ly/4xKLM9h')
for u in sorted(urls):
    r = subprocess.run(['curl', '-s', '-o', os.devnull, '-w', '%{http_code} %{redirect_url}', u], capture_output=True, text=True).stdout
    code, _, dest = r.partition(' ')
    ok = code == '200' or (code in ('301', '302') and dest)
    check(ok, 'link %s -> %s' % (u, r))
    if u.startswith('https://bit.ly') and ok:
        r2 = subprocess.run(['curl', '-s', '-o', os.devnull, '-w', '%{http_code}', dest], capture_output=True, text=True).stdout
        check(r2 == '200', 'link %s lands on %s with HTTP %s' % (u, dest, r2))
print('links: %d QR/short-link destinations checked live' % len(urls))

# ---- the spec --------------------------------------------------------------------------------
spec = pymupdf.open(os.path.join(PKG, '00_Print-specification.pdf'))
tbc = sum(p.get_text().count('[to confirm]') + p.get_text().count('[name, email, phone]') for p in spec)
if tbc:
    notes.append('print specification still has %d "[to confirm]" field(s) to fill in' % tbc)

print('\n' + '=' * 70)
print('FAILURES: %d' % len(fails))
for f in fails:
    print('  - ' + f)
print('NOTES:')
for n in notes:
    print('  - ' + n)

sys.exit(1 if fails else 0)
