"""Printer hand-off package: print specification PDF + one clearly named PDF per card, zipped."""
import glob, os, shutil, zipfile
import pymupdf

import paths
PR = paths.PRINT_READY
PKG = paths.PACKAGE
FONTS = paths.FONTS
PT = 72 / 25.4
A4W, A4H = 210 * PT, 297 * PT
M = 18 * PT

CARDS = [  # (source pattern, card, front, back, package file name)
    ('English*', 1, 'English Intermediate &amp; Advanced Conversation Hours', 'Visit our Study Centre',
     'Card-1_English-Conversation-Hours__Visit-our-Study-Centre'),
    ('French*', 2, 'French, German &amp; Spanish Intermediate Conversation Hours',
     'French, German &amp; Spanish Advanced Conversation Hours',
     'Card-2_FGS-Intermediate__FGS-Advanced-Conversation-Hours'),
    ('Friends*', 3, 'Friends Without Frontiers', 'Conversation Exchange',
     'Card-3_Friends-Without-Frontiers__Conversation-Exchange'),
    ('Language*', 4, 'Language Advising', 'Study Abroad', 'Card-4_Language-Advising__Study-Abroad'),
    ('Portuguese*', 5, 'Portuguese Intermediate &amp; Advanced Conversation Hours', 'Visit our Study Centre',
     'Card-5_Portuguese-Conversation-Hours__Visit-our-Study-Centre'),
]
SUFFIX = '_A6_double-sided_v7.pdf'

CSS = """
@font-face { font-family: os; src: url(OpenSans-Regular.ttf); }
@font-face { font-family: os; src: url(OpenSans-Bold.ttf); font-weight: bold; }
@font-face { font-family: fj; src: url(Feijoa-Bold.otf); }
* { font-family: os; color: #101f2a; }
body { font-size: 9.5pt; line-height: 1.4; }
h1 { font-family: fj; font-size: 20pt; margin: 0 0 2pt 0; color: #133844; }
h2 { font-size: 11pt; margin: 9pt 0 3pt 0; color: #133844; }
p { margin: 0 0 5pt 0; }
ul { margin: 0 0 5pt 0; padding-left: 14pt; }
li { margin-bottom: 2pt; }
table { border-collapse: collapse; width: 100%; }
td, th { border: 0.6pt solid #9fb3b0; padding: 3pt 5pt; vertical-align: top; font-size: 9pt; }
th { background-color: #e3efec; text-align: left; }
.tbc { background-color: #fff3c4; }
.small { font-size: 8.5pt; color: #44525c; }
.file { font-size: 8.5pt; }
"""
archive = pymupdf.Archive(FONTS)


def html(page, rect, body):
    page.insert_htmlbox(rect, body, css=CSS, archive=archive)


# ---- copy and rename the print files -------------------------------------------------
if os.path.isdir(PKG):
    shutil.rmtree(PKG)
os.makedirs(PKG)
files = []
for pat, n, front, back, name in CARDS:
    src = sorted(glob.glob(os.path.join(PR, pat + '_%s_QR20_print.pdf' % paths.VERSION)))
    assert len(src) == 1, (pat, src)
    dst = os.path.join(PKG, name + SUFFIX)
    shutil.copyfile(src[0], dst)
    files.append(dst)

# facts for the spec, read from the files themselves
d0 = pymupdf.open(files[0])[0]
sheet = (d0.mediabox.width / PT, d0.mediabox.height / PT)
trim = (d0.trimbox.width / PT, d0.trimbox.height / PT)
bleed = (d0.bleedbox.width - d0.trimbox.width) / 2 / PT
mindpi = 9999
for f in files:
    d = pymupdf.open(f)
    for p in d:
        for im in p.get_images(full=True):
            for r in p.get_image_rects(im[0]):
                if r.width > 5 and r.height > 5:
                    mindpi = min(mindpi, im[2] / (r.width / 72.0))

rows = ''.join('<tr><td>%d</td><td class="file">%s</td><td>%s</td><td>%s</td><td class="tbc">&nbsp;</td></tr>'
               % (n, name + SUFFIX, front, back) for (pat, n, front, back, name) in CARDS)

doc = pymupdf.open()
p = doc.new_page(width=A4W, height=A4H)
html(p, pymupdf.Rect(M, M, A4W - M, A4H - 14 * PT), """
<h1>Print specification</h1>
<p><b>University of Cambridge Language Centre &middot; postcards &middot; 5 double-sided cards</b></p>

<h2>Job</h2>
<table>
<tr><th style="width:26%%">Items</th><td style="width:74%%">5 different cards, each printed on both sides</td></tr>
<tr><th style="width:26%%">Finished size</th><td style="width:74%%">A6 landscape, %.0f &times; %.0f mm</td></tr>
<tr><th style="width:26%%">Printing</th><td style="width:74%%">Full colour both sides (4/4)</td></tr>
<tr><th style="width:26%%">Orientation</th><td style="width:74%%">Both sides are supplied upright. Please print <b>head-to-head</b>: turning the card over
left-to-right (like a book page) shows the back the right way up.</td></tr>
<tr><th style="width:26%%">Quantity</th><td style="width:74%%" class="tbc">Per card &ndash; see the table below [to confirm]</td></tr>
<tr><th style="width:26%%">Stock and finish</th><td style="width:74%%" class="tbc">[to confirm]</td></tr>
<tr><th style="width:26%%">Delivery date and address</th><td style="width:74%%" class="tbc">[to confirm]</td></tr>
<tr><th style="width:26%%">Contact</th><td style="width:74%%" class="tbc">[name, email, phone]</td></tr>
</table>

<h2>Files</h2>
<p>One PDF per card: <b>page 1 = front, page 2 = back</b>. Please print from these files.</p>
<table>
<tr><th style="width:6%%">Card</th><th style="width:34%%">File</th><th style="width:22%%">Front (page 1)</th><th style="width:22%%">Back (page 2)</th><th style="width:16%%">Quantity</th></tr>
%s
</table>
<p class="small">Cards 1 and 5 have the same back (Visit our Study Centre); each is a separate card with its own front.</p>

<h2>Artwork</h2>
<ul>
<li><b>Bleed and marks:</b> %.0f mm bleed on all sides; crop marks outside the bleed. Page size %.0f &times; %.0f mm,
with TrimBox (%.0f &times; %.0f mm) and BleedBox set.</li>
<li><b>Fonts:</b> all embedded (Open Sans, Feijoa).</li>
<li><b>Images:</b> at least %.0f dpi at printed size.</li>
<li><b>Colour:</b> supplied as the designer's full-colour artwork (a mix of RGB and CMYK). Please convert with your
standard press profile. The University of Cambridge logo includes Pantone spot colour definitions (PANTONE 109 C,
PANTONE Black C, PANTONE Red 032 C): please print these as <b>CMYK process</b>, not as extra spot inks.</li>
<li><b>QR codes:</b> 20 &times; 20 mm, vector, <b>100%% black (K only)</b>. Please keep them K-only (no rich black) and
do not rescale or move them. The small logo in each code's centre is intentional.</li>
</ul>

<h2>Proof</h2>
<p>Please send a PDF proof before printing and, if possible, one printed proof of each card. We will scan-test the QR
codes on the printed proof.</p>
""" % (trim[0], trim[1], rows, bleed, sheet[0], sheet[1], trim[0], trim[1], mindpi))

# ---- page 2: what each card looks like, front and back -------------------------------
p = doc.new_page(width=A4W, height=A4H)
html(p, pymupdf.Rect(M, M, A4W - M, M + 16 * PT),
     '<h1>Cards at a glance</h1><p>Front on the left, back on the right. Shown reduced; the PDFs are at full size.</p>')
TW = 60 * PT
TH = TW * 105 / 148
y = M + 22 * PT
for (pat, n, front, back, name), f in zip(CARDS, files):
    src = pymupdf.open(sorted(glob.glob(os.path.join(paths.CARDS, pat + '.pdf')))[0])
    html(p, pymupdf.Rect(M, y + TH / 2 - 6 * PT, M + 12 * PT, y + TH / 2 + 6 * PT), '<h2>%d</h2>' % n)
    for j in range(2):
        x = M + 14 * PT + j * (TW + 8 * PT)
        r = pymupdf.Rect(x, y, x + TW, y + TH)
        p.show_pdf_page(r, src, j)
        p.draw_rect(r, color=(0.62, 0.70, 0.69), width=0.4)
        html(p, pymupdf.Rect(x, r.y1 + 0.8 * PT, x + TW, r.y1 + 6 * PT),
             '<p class="small"><b>%s:</b> %s</p>' % ('Front' if j == 0 else 'Back', front if j == 0 else back))
    y += TH + 8.5 * PT

doc.set_metadata({'title': 'Print specification: Language Centre postcards', 'author': 'University of Cambridge Language Centre'})
spec = os.path.join(PKG, '00_Print-specification.pdf')
doc.rewrite_images(dpi_threshold=200, dpi_target=180, quality=82, lossy=True, lossless=True, bitonal=False, color=True, gray=True)
doc.save(spec, garbage=4, deflate=True)   # no clean=True (breaks the spot-colour logo in pdfium)

zpath = PKG + '.zip'
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(PKG)):
        z.write(os.path.join(PKG, fn), os.path.join(os.path.basename(PKG), fn))
for fn in sorted(os.listdir(PKG)):
    print('  %-80s %5.1f MB' % (fn, os.path.getsize(os.path.join(PKG, fn)) / 1e6))
print('zip: %s  %.1f MB' % (zpath, os.path.getsize(zpath) / 1e6))
print('min image dpi %.0f; sheet %.0fx%.0f trim %.0fx%.0f bleed %.1f' % (mindpi, sheet[0], sheet[1], trim[0], trim[1], bleed))
