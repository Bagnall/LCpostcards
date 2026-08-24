"""Generate the header band textures from the designer's artwork.

The 2026 postcards place one Cambridge "expressive" texture full-bleed behind
each card; the header band is the top slice of it, with the middle of the card
covered by paper. This script reproduces that slice as a web image.

Footers are left as the flat theme teal. The printed footers are the bottom
slice of the same texture, but several run dark on one side and pale on the
other, so no single text colour clears WCAG AA across them.

The supplied files are CMYK print JPEGs tagged Coated FOGRA39. Browsers cannot
render CMYK JPEGs, and a naive channel conversion turns the brand teal green,
so each one is converted to sRGB through its embedded profile.

Usage (from the repo root, with design/ populated from the designer's archive):

    pip install pillow
    python scripts/build-band-textures.py

Outputs public/assets/bands/<page>.webp, and reports the luminance of each
band's left and right edge so the themes can pick a wordmark plate and URL
colour that clear WCAG AA against it.
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

WIDTH = 1920          # wide enough for a full-bleed band on a large display
QUALITY = 80

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
    """Mean relative luminance of a region, for contrast decisions."""
    patch = band.crop(box).convert('RGB').resize((10, 4), Image.LANCZOS)
    px = list(patch.get_flattened_data() if hasattr(patch, 'get_flattened_data')
              else patch.getdata())
    return sum(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in px) / len(px) / 255


def on_white(lum):
    """Contrast ratio of white text over a background of this luminance."""
    return 1.05 / (lum + 0.05)


def on_ink(lum):
    """Contrast ratio of the ink colour (#10222c) over this luminance."""
    return (lum + 0.05) / (0.045 + 0.05)


def main():
    if not os.path.isdir(SRC):
        sys.exit('%s not found — populate design/ from the designer archive first.' % SRC)
    os.makedirs(DST, exist_ok=True)
    total = 0
    print('%-32s %-30s %s' % ('page', 'left (wordmark)', 'right (URL)'))
    for slug, rel in PAGES.items():
        band = slice_band(to_srgb(os.path.join(SRC, rel)), HEADER)
        out = os.path.join(DST, '%s.webp' % slug)
        band.save(out, 'WEBP', quality=QUALITY, method=6)
        total += os.path.getsize(out)

        w, h = band.size
        left = luminance(band, (0, 0, int(w * 0.28), h))
        right = luminance(band, (int(w * 0.66), 0, w, h))
        print('%-32s L=%.2f %-22s R=%.2f %s' % (
            slug, left,
            'white ok' if on_white(left) >= 4.5
            else 'plate (white %.1f:1)' % on_white(left),
            right,
            'ink' if on_ink(right) >= 4.5 else 'white'))
    print('\n%d files, %.0f KB total' % (len(PAGES), total / 1024))


if __name__ == '__main__':
    main()
