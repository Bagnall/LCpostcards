"""Where everything lives, relative to the repository. Every print script imports this."""
import os

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PRINT = os.path.dirname(SCRIPTS)
REPO = os.path.dirname(PRINT)

DESIGNER = os.path.join(PRINT, 'source', 'designer')     # the designer's 2-page PDFs (one per card)
LOGOS = os.path.join(PRINT, 'source', 'logos')           # LC logo SVGs (black, white)
FONTS = os.path.join(REPO, 'fonts-src')                  # shared with the website build

BUILD = os.path.join(PRINT, 'build')                     # intermediates, git-ignored
CARDS = os.path.join(BUILD, 'cards')                     # edited cards at trim size
PRINT_READY = os.path.join(BUILD, 'print-ready')         # with bleed and crop marks

VERSION = 'v7'
PACKAGE = os.path.join(PRINT, 'package-%s' % VERSION)    # what goes to the printer
REVIEW = os.path.join(PRINT, 'review', 'Postcards-%s-text-and-QR-review.pdf' % VERSION)

for d in (BUILD, CARDS, PRINT_READY):
    os.makedirs(d, exist_ok=True)
