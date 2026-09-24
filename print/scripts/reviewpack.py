"""Review pack for non-technical staff: text proofreading and QR testing.

A4 portrait. Page 1: how to review. Then one card per page,
drawn from the final print artwork at exactly 100% (vector, so the QR codes scan
from paper or screen), with what each code and link should open, and space for
comments.
"""
import glob, os
import pymupdf

import paths
S = paths.BUILD
FONTS = paths.FONTS
OUT = paths.REVIEW
os.makedirs(os.path.dirname(OUT), exist_ok=True)
PT = 72 / 25.4
A4W, A4H = 210 * PT, 297 * PT
M = 18 * PT                                     # page margin

BOOKING = ('bit.ly/4xKLM9h', 'the Language Centre <b>Speaking Practice</b> page, where you book a place')
MOODLE = ('bit.ly/4htBwMy', 'the <b>Study Abroad</b> course on Moodle. It will ask you to log in with your Cambridge account; that is expected')

# (file pattern, page, side, card title, short link, page the QR/short link opens, other links)
CARDS = [
    ('English*', 0, 'front', 'English Intermediate &amp; Advanced Conversation Hours', 'eng-conv',
     'English Intermediate and Advanced Conversation Hours', [BOOKING]),
    ('English*', 1, 'back', 'Visit our Study Centre', 'lc-visit', 'Visit our Study Centre', []),
    ('French*', 0, 'front', 'French, German &amp; Spanish Intermediate Conversation Hours', 'inter-conv',
     'French, German and Spanish Intermediate Conversation Hours', [BOOKING]),
    ('French*', 1, 'back', 'French, German &amp; Spanish Advanced Conversation Hours', 'adv-conv',
     'French, German and Spanish Advanced Conversation Hours', [BOOKING]),
    ('Friends*', 0, 'front', 'Friends Without Frontiers', 'lc-friends', 'Friends Without Frontiers', [BOOKING]),
    ('Friends*', 1, 'back', 'Conversation Exchange', 'conv-exch', 'Conversation Exchange', []),
    ('Language*', 0, 'front', 'Language Advising', 'lc-adv', 'Language Advising', []),
    ('Language*', 1, 'back', 'Study Abroad', 'lc-abroad', 'Study Abroad', []),
    ('Portuguese*', 0, 'front', 'Portuguese Intermediate and Advanced Conversation Hours', 'port-conv',
     'Portuguese Intermediate and Advanced Conversation Hours', [BOOKING]),
    ('Portuguese*', 1, 'back', 'Visit our Study Centre', 'lc-visit', 'Visit our Study Centre', []),
]

CSS = """
@font-face { font-family: os; src: url(OpenSans-Regular.ttf); }
@font-face { font-family: os; src: url(OpenSans-Bold.ttf); font-weight: bold; }
@font-face { font-family: fj; src: url(Feijoa-Bold.otf); }
* { font-family: os; color: #101f2a; }
body { font-size: 10.5pt; line-height: 1.45; }
h1 { font-family: fj; font-size: 22pt; margin: 0 0 4pt 0; color: #133844; }
h2 { font-size: 12.5pt; margin: 12pt 0 3pt 0; color: #133844; }
p { margin: 0 0 6pt 0; }
ol, ul { margin: 0 0 6pt 0; padding-left: 16pt; }
li { margin-bottom: 3pt; }
.lead { font-size: 11.5pt; }
.note { background-color: #eef6f4; padding: 6pt 8pt; }
.small { font-size: 9pt; color: #44525c; }
.tag { font-size: 9pt; color: #44525c; }
.cardtitle { font-family: fj; font-size: 15pt; color: #133844; margin: 0; }
table { border-collapse: collapse; width: 100%; }
td, th { border: 0.6pt solid #9fb3b0; padding: 3pt 4pt; font-size: 9pt; vertical-align: top; }
th { background-color: #e3efec; text-align: left; }
.tick { width: 34pt; text-align: center; }
"""

archive = pymupdf.Archive(FONTS)


def html(page, rect, body):
    page.insert_htmlbox(rect, body, css=CSS, archive=archive)


def footer(page, n, total):
    html(page, pymupdf.Rect(M, A4H - 12 * PT, A4W - M, A4H - 5 * PT),
         '<p class="small">Language Centre postcards &middot; text and QR review &middot; page %d of %d</p>' % (n, total))


doc = pymupdf.open()
total = 1 + len(CARDS)

# ---- page 1: how to review ----------------------------------------------------
p = doc.new_page(width=A4W, height=A4H)
html(p, pymupdf.Rect(M, M, A4W - M, A4H - 16 * PT), """
<h1>Postcards: please check the text and the QR codes</h1>
<p class="lead">We are about to print new Language Centre postcards. Before they go to the printer, we would
like a second pair of eyes on the <b>wording</b> and on the <b>QR codes and links</b>.
It should take about 15 minutes.</p>

<p class="note">The design and layout have already been agreed, so there is no need to comment on colours,
pictures or where things sit on the card. We are only asking about the words and the links.</p>

<h2>What is in this document</h2>
<p>There are <b>five cards, each printed on both sides</b>. Each side has its own page (ten pages in all),
shown at its real printed size (A6, about the size of a standard postcard). Under each side is a short list of
what to check.</p>

<h2>1. Read the words</h2>
<ul>
<li>Spelling, grammar and punctuation.</li>
<li>Facts: prices (&pound;35 / &pound;45 / &pound;55), opening hours, levels (B1+, C1+), the phone number,
email address and postal address.</li>
<li>Anything that is out of date, unclear or missing.</li>
</ul>

<h2>2. Scan each QR code with your phone</h2>
<ol>
<li>Open your phone's camera and point it at the QR code (the black-and-white square, bottom right of the card).
Most phones show a link to tap; you do not need a special app.</li>
<li>Tap the link. Check that the page that opens has the heading listed under the card.</li>
</ol>
<p><b>If printing</b>, choose <b>"Actual size"</b> (not "Fit to page") so the cards come out at their real size;
this is the best test, because it is how people will use the real cards.</p>
<p><b>If scanning from a screen</b>, zoom the document to <b>200% or more</b> first. At normal zoom the code is too
small on screen for a phone to read. That is expected, and it does not mean the code is faulty.</p>

<h2>3. Try the short links</h2>
<p>Each card also prints short web addresses beginning <b>bit.ly/</b> for people who would rather type than scan.
Type one or two into a web browser and check they open the page listed. The letters after <b>bit.ly/</b> are
case-sensitive, so type capitals as capitals.</p>

<h2>How to send your comments</h2>
<p>Reply to the email with the <b>card number and side</b> (shown at the top of each page) and what you noticed,
for example: <i>"Card 2 front: typo in the second paragraph"</i> or <i>"Card 4 back: the QR code opened the wrong page"</i>.
If everything is fine, a quick "all OK" is really helpful too.</p>
<p class="small">"Visit our Study Centre" is the back of both Card 1 and Card 5. You only need to read it once,
but please scan both codes.</p>
""")
footer(p, 1, total)

# ---- one page per card ----------------------------------------------------------
CW, CH = 148 * PT, 105 * PT
for i, (pat, pno, side, title, short, dest, others) in enumerate(CARDS):
    cardno = i // 2 + 1
    tag = 'Card %d &middot; %s' % (cardno, side)
    src = pymupdf.open(sorted(glob.glob(os.path.join(paths.CARDS, pat + '.pdf')))[0])
    p = doc.new_page(width=A4W, height=A4H)
    html(p, pymupdf.Rect(M, M, A4W - M, M + 20 * PT),
         '<p class="tag">%s (card %d of 5, printed on both sides)</p><p class="cardtitle">%s</p>' % (tag, cardno, title))
    x0 = (A4W - CW) / 2
    y0 = M + 22 * PT
    card = pymupdf.Rect(x0, y0, x0 + CW, y0 + CH)
    p.show_pdf_page(card, src, pno)                         # exact size, vector
    p.draw_rect(card, color=(0.62, 0.70, 0.69), width=0.5)
    html(p, pymupdf.Rect(x0, card.y1 + 1.5 * PT, x0 + CW, card.y1 + 6 * PT),
         '<p class="small">Shown at actual printed size: 148 &times; 105 mm.</p>')
    items = ['<li><b>Read the words</b> on this side of the card, shown above.</li>',
             '<li><b>Scan the QR code.</b> It should open a page headed <b>"%s"</b>.</li>' % dest,
             '<li><b>Type bit.ly/%s</b> (printed above the QR code). It should open the same page.</li>' % short]
    for link, what in others:
        items.append('<li><b>Type %s</b> (in the text). It should open %s.</li>' % (link, what))
    if i == 9:
        items.append('<li class="small">Same words as the back of Card 1; you only need to read it once, but please scan this code too.</li>')
    ty = card.y1 + 9 * PT
    box_top = html(p, pymupdf.Rect(x0, ty, x0 + CW, ty + 60 * PT),
                   '<h2 style="margin-top:0">Check</h2><ol>%s</ol>' % ''.join(items))
    # comments box with ruled lines
    cy0, cy1 = A4H - 70 * PT, A4H - 16 * PT
    html(p, pymupdf.Rect(x0, cy0 - 7 * PT, x0 + CW, cy0), '<p><b>Your comments on %s</b></p>' % tag)
    p.draw_rect(pymupdf.Rect(x0, cy0, x0 + CW, cy1), color=(0.62, 0.70, 0.69), width=0.5)
    y = cy0 + 9 * PT
    while y < cy1 - 3 * PT:
        p.draw_line(pymupdf.Point(x0 + 4 * PT, y), pymupdf.Point(x0 + CW - 4 * PT, y), color=(0.82, 0.86, 0.86), width=0.4)
        y += 8 * PT
    footer(p, i + 2, total)

doc.set_metadata({'title': 'Language Centre postcards: text and QR review', 'author': 'Language Centre',
                  'subject': 'Review pack for proofreading the postcard text and testing the QR codes'})
doc.rewrite_images(dpi_threshold=200, dpi_target=180, quality=82, lossy=True, lossless=True,
                   bitonal=False, color=True, gray=True)       # background photos only; QR and text are vector
doc.save(OUT, garbage=4, deflate=True)   # no clean=True: it rewrites content streams and breaks the spot-colour lockup in pdfium
print(OUT, doc.page_count, 'pages', round(os.path.getsize(OUT) / 1e6, 1), 'MB')
