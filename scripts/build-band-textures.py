"""Generate the header and footer band textures from the designer's artwork.

The 2026 postcards place one Cambridge "expressive" texture full-bleed behind
each card. The header band is the top slice of it and the footer band the
bottom slice, with the middle of the card covered by paper. This script cuts
both slices as web images.

The supplied files are CMYK print JPEGs tagged Coated FOGRA39. Browsers cannot
render CMYK JPEGs, and a naive channel conversion turns the brand teal green,
so each one is converted to sRGB through its embedded profile.

It also reports, per band and per side, whether white or dark text clears WCAG
AA against the artwork. That is what picks the Cambridge wordmark variant and
the text colours in the .theme-* blocks in src/styles/main.css. The cards do
the same thing: the reversed wordmark on dark bands, the positive one on pale.

Usage (from the repo root, with design/ populated from the designer's archive):

    pip install pillow
    python scripts/build-band-textures.py
"""

import io
import os
import sys

from PIL import Image, ImageCms

SRC = os.path.join('design', 'assets', 'Postcard Assets')
DST = os.path.join('public', 'assets', 'bands')

# A5 and A4 landscape share the same 1.414 ratio, so the texture maps 1:1 onto
# the card. These fractions are where the paper body starts and ends, measured
# off the printed cards.
HEADER = (0.0, 0.202)
FOOTER = (0.862, 1.0)

WIDTH = 1920          # wide enough for a full-bleed band on a large display
QUALITY = 80

# Relative luminance of the two wordmark variants' text, for contrast maths.
WHITE_TEXT = 1.0
DARK_TEXT = 0.025     # the near-black in ucam_language_centre_h_black.png
AA = 4.5

# page slug -> texture, one per printed card side
PAGES = {
    'english-conversation-hours':
        'EnglishConversationHours_VisitOurStudyCentre/ucam_max_expression_grad_a4_3.jpg',
    'visit-our-study-centre':
        'EnglishConversationHours_VisitOurStudyCentre/ucam_expressive_1_a4_upside_down.jpg',
    'intermediate-conversation-hours':
        'FrenchGermanAndSpanishConversationHoursIntermediate/ucam_a4_mid4.jpg',
    'advanced-conversation-hours':
        'FrenchGermanAndSpanishConversationHoursIntermediate/ucam_max_expression_grad_a4_2.jpg',
    'friends-without-frontiers':
        'FriendsWithoutFrontiers_Conversation Exchange/ucam_expressive_full_size1_a4.jpg',
    'conversation-exchange':
        'FriendsWithoutFrontiers_Conversation Exchange/ucam_max_expression_a4_4.jpg',
    'language-advising':
        'LanguageAdvising_StudyAbroad/ucam_max_expression_grad_a4_3.jpg',
    'study-abroad':
        'LanguageAdvising_StudyAbroad/ucam_expressive_1_a4.jpg',
    'portuguese-conversation-hours':
        'PortugueseConversationHoursIntermediateAndAdvanced_VisitOurStudyCentre/ucam_a4_mid1.jpg',
    # The index has no printed card; it borrows the spare Study Centre texture.
    'index':
        'PortugueseConversationHoursIntermediateAndAdvanced_VisitOurStudyCentre/ucam_simple_4_upside_down.jpg',
}

# Where each piece of text sits within its band, as fractions of the band box.
# Mirrors the layout in src/scripts/components.js.
REGIONS = {
    'header': {
        'left':  (0.04, 0.26, 0.30, 0.70),   # Cambridge wordmark, centred
        'right': (0.74, 0.99, 0.20, 0.45),   # site URL, near the top
    },
    'footer': {
        'left':  (0.04, 0.30, 0.05, 0.60),   # tagline and logo row
        'right': (0.66, 0.99, 0.05, 0.55),   # contact details
    },
}

SRGB = ImageCms.createProfile('sRGB')


def to_srgb(path):
    """Open a print JPEG and convert it to sRGB through its embedded profile."""
    im = Image.open(path)
    icc = im.info.get('icc_profile')
    if im.mode == 'CMYK' and icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        return ImageCms.profileToProfile(
            im, src, SRGB, outputMode='RGB',
            renderingIntent=ImageCms.Intent.PERCEPTUAL)
    return im.convert('RGB')


def slice_band(im, span):
    w, h = im.size
    top, bottom = int(round(h * span[0])), int(round(h * span[1]))
    band = im.crop((0, top, w, bottom))
    return band.resize((WIDTH, max(1, round(WIDTH * band.size[1] / w))),
                       Image.LANCZOS)


def luminance(band, box):
    """Worst-case (lightest and darkest) relative luminance across a region.

    Both are needed: text has to clear AA against the whole area it sits on,
    not just its average, and several bands change tone mid-side.
    """
    patch = band.crop(box).convert('RGB').resize((12, 6), Image.LANCZOS)
    vals = [(0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            for r, g, b in patch.getdata()]
    return min(vals), max(vals)


def bottom_colour(band):
    """The strip's bottom edge, as a hex colour, for the footer to extend."""
    w, h = band.size
    row = band.crop((0, h - 3, w, h)).convert('RGB').resize((1, 1), Image.LANCZOS)
    return '#%02x%02x%02x' % row.getpixel((0, 0))


def ratio(text_lum, bg_lum):
    hi, lo = max(text_lum, bg_lum), min(text_lum, bg_lum)
    return (hi + 0.05) / (lo + 0.05)


def pick(lo, hi):
    """Choose white or dark text for a region, worst case over its tonal range."""
    white = min(ratio(WHITE_TEXT, lo), ratio(WHITE_TEXT, hi))
    dark = min(ratio(DARK_TEXT, lo), ratio(DARK_TEXT, hi))
    if white >= dark:
        return 'white', white
    return 'dark', dark


def main():
    if not os.path.isdir(SRC):
        sys.exit('%s not found — populate design/ from the designer archive first.' % SRC)
    os.makedirs(DST, exist_ok=True)

    total = 0
    print('%-32s %-22s %-22s %-22s %s'
          % ('page', 'header left (wordmark)', 'header right (URL)',
             'footer left', 'footer right'))
    fails = []
    bases = {}
    for slug, rel in PAGES.items():
        im = to_srgb(os.path.join(SRC, rel))
        cells = []
        for kind, span in (('header', HEADER), ('footer', FOOTER)):
            band = slice_band(im, span)
            out = os.path.join(DST, '%s-%s.webp' % (slug, kind))
            band.save(out, 'WEBP', quality=QUALITY, method=6)
            total += os.path.getsize(out)

            w, h = band.size
            # Sample only where the text actually lands, not the whole half:
            # several bands change tone mid-side, and averaging over the change
            # gives an answer that is wrong for both parts of it.
            regions = REGIONS[kind]
            for side, frac in regions.items():
                x0, x1, y0, y1 = frac
                box = (int(w * x0), int(h * y0), int(w * x1), int(h * y1))
                choice, r = pick(*luminance(band, box))
                cells.append('%s %.1f:1%s' % (choice, r, '' if r >= AA else ' !'))
                if r < AA:
                    fails.append('%s %s %s: best is %s at %.1f:1'
                                 % (slug, kind, side, choice, r))

            if kind == 'footer':
                # The footer paints the strip full-width at its top edge so the
                # printed notch survives, and fills the rest with this colour —
                # the strip's own bottom edge. Needed because the footer grows
                # taller than the strip's aspect, especially on mobile.
                bases[slug] = bottom_colour(band)
        print('%-32s %-22s %-22s %-22s %s' % (slug, *cells))

    print('\n%d files, %.0f KB total' % (len(PAGES) * 2, total / 1024))

    print("\n--footer-base per theme (the strip's bottom edge):")
    for slug, hexc in bases.items():
        print('  %-32s %s' % (slug, hexc))

    if fails:
        print('\nBelow AA — needs a scrim or a copy change:')
        for f in fails:
            print('  ' + f)


if __name__ == '__main__':
    main()
