"""v4 postcards (v3 + full-URL QR codes with the LC logo centred): 20mm QR bottom-right, short links, text wrapped around the code.

Line handling: each original line is kept as its own line (so bullet lists and
deliberate breaks survive). A line is merged with the next only when the break is
mid-token - the line ends in '/', '-' or '.' and the next starts lower-case - which
is how the long booking URLs were broken. A line too wide for its measure is
soft-wrapped; a line containing a single token too wide to fit is reported rather
than silently overlapped.
"""
import glob, os
import pymupdf
from qrlogo import draw_qr, LONG

import paths
D = paths.DESIGNER
S = paths.BUILD
FONTS = paths.FONTS
OUTDIR = paths.CARDS
os.makedirs(OUTDIR, exist_ok=True)

PT = 72.0 / 25.4
QR_SIZE, QR_RIGHT, QR_BOTTOM = 20.0, 141.0, 88.1
QR_X0, QR_Y0 = QR_RIGHT - QR_SIZE, QR_BOTTOM - QR_SIZE
GUTTER, FULL_RIGHT = 3.0, 141.6
TOP_PAD = 2.2   # keep glyph descenders/ascenders out of the code's quiet zone
BOTTOM_LIMIT, TOP_LIMIT, COL_X = 89.2, 24.5, 70.0

SHORT = {
    ('EnglishConversationHours_VisitOurStudyCentre', 0): 'eng-conv',
    ('EnglishConversationHours_VisitOurStudyCentre', 1): 'lc-visit',
    ('FrenchGermanAndSpanishConversationHoursIntermediate_Advanced', 0): 'inter-conv',
    ('FrenchGermanAndSpanishConversationHoursIntermediate_Advanced', 1): 'adv-conv',
    ('FriendsWithoutFrontiers_Conversation Exchange', 0): 'lc-friends',
    ('FriendsWithoutFrontiers_Conversation Exchange', 1): 'conv-exch',
    ('LanguageAdvising_StudyAbroad', 0): 'lc-adv',
    ('LanguageAdvising_StudyAbroad', 1): 'lc-abroad',
    ('PortugueseConversationHoursIntermediateAndAdvanced_VisitOurStudyCentre', 0): 'port-conv',
    ('PortugueseConversationHoursIntermediateAndAdvanced_VisitOurStudyCentre', 1): 'lc-visit',
}
FONTFILE = {'OpenSans': 'OpenSans-Regular.ttf', 'OpenSans-Bold': 'OpenSans-Bold.ttf',
            'OpenSans-SemiBold': 'OpenSans-SemiBold.ttf', 'Feijoa-Bold': 'Feijoa-Bold.otf'}
_cache = {}


def font_for(name):
    key = name.split('+')[-1]
    fn = FONTFILE.get(key)
    if fn is None:
        for k, v in FONTFILE.items():
            if k.lower() in key.lower():
                fn = v
                break
    fn = fn or 'OpenSans-Regular.ttf'
    if fn not in _cache:
        p = os.path.join(FONTS, fn)
        _cache[fn] = (pymupdf.Font(fontfile=p), p, os.path.splitext(fn)[0])
    return _cache[fn]


def rgb(c):
    return ((c >> 16 & 255) / 255.0, (c >> 8 & 255) / 255.0, (c & 255) / 255.0)


def raw_lines(block):
    out = []
    for ln in block['lines']:
        chars = []
        for sp in ln['spans']:
            for ch in sp['text']:
                chars.append((ch, sp))
        out.append(chars)
    return out


def merge_midtoken(lines):
    """Join a line to the next only when the break splits a token (URLs)."""
    out, i = [], 0
    while i < len(lines):
        cur = list(lines[i])
        while i + 1 < len(lines):
            txt = ''.join(c for c, _ in cur)
            nxt = ''.join(c for c, _ in lines[i + 1]).strip()
            if (txt and not txt[-1].isspace() and nxt
                    and txt.rstrip()[-1:] in ('/', '-', '.')
                    and (nxt[0].islower() or nxt[0] == '/')):
                cur = cur + list(lines[i + 1])
                i += 1
            else:
                break
        out.append(cur)
        i += 1
    return out


def to_words(chars, short):
    words, cur = [], []
    for ch, sp in list(chars) + [(' ', None)]:
        if ch.isspace():
            if cur:
                words.append(dict(t=''.join(c for c, _ in cur), sp=cur[0][1]))
                cur = []
        else:
            cur.append((ch, sp))
    # never let a bullet sit alone at the end of a line
    glued, i = [], 0
    while i < len(words):
        if words[i]['t'] in ('•', '·', '-') and i + 1 < len(words):
            nxt = words[i + 1]
            glued.append(dict(t=words[i]['t'] + ' ' + nxt['t'], sp=nxt['sp']))
            i += 2
        else:
            glued.append(words[i])
            i += 1
    words = glued
    subs = 0
    for w in words:
        low = w['t'].lower().rstrip('.')
        if 'langcen.cam.ac.uk/advising/speaking-practice' in low or low == 'www.langcen.cam.ac.uk/':
            w['t'] = 'bit.ly/' + short + ('.' if w['t'].endswith('.') else '')
            subs += 1
    return words, subs


def split_token(w, avail):
    """Break an over-long URL-ish token after '/' so it can wrap."""
    t = w['t']
    if font_for(w['sp']['font'])[0].text_length(t, w['sp']['size']) / PT <= avail:
        return [w]
    f0 = font_for(w['sp']['font'])[0]

    def chop(breaks):
        out, cur = [], ''
        for ch in t:
            cur += ch
            if ch in breaks and cur:
                out.append(cur)
                cur = ''
        if cur:
            out.append(cur)
        return out

    parts = chop('/')
    if len(parts) < 2 or max(f0.text_length(x, w['sp']['size']) / PT for x in parts) > avail:
        wider = chop('/@')
        if len(wider) > 1 and max(f0.text_length(x, w['sp']['size']) / PT
                                  for x in wider) <= avail:
            parts = wider
    if len(parts) < 2:
        return [w]
    out, buf = [], ''
    f = font_for(w['sp']['font'])[0]
    for p in parts:
        trial = buf + p
        if buf and f.text_length(trial, w['sp']['size']) / PT > avail:
            out.append(dict(t=buf, sp=w['sp'], nosp=True))
            buf = p
        else:
            buf = trial
    if buf:
        out.append(dict(t=buf, sp=w['sp'], nosp=True))
    return out


def wtext(w):
    return font_for(w['sp']['font'])[0].text_length(w['t'], w['sp']['size']) / PT


def wspace(w):
    return font_for(w['sp']['font'])[0].text_length(' ', w['sp']['size']) / PT


def measure(y, lead):
    return (QR_X0 - GUTTER) if not (y + lead < QR_Y0 - TOP_PAD or y > QR_BOTTOM) else FULL_RIGHT


def lay_block(logical, x0, top, lead):
    """Place logical lines, soft-wrapping any that are too wide. Returns
    (placed_lines, bottom, overflow_tokens)."""
    placed, y, bad = [], top, []
    for words0 in logical:
        if not words0:
            continue
        queue = list(words0)
        cur, wid = [], 0.0
        while queue:
            w = queue.pop(0)
            add = wtext(w) + (wspace(w) if (cur and not w.get('nosp')) else 0.0)
            m = measure(y, lead)
            if not cur and x0 + wtext(w) > m + 0.01:
                frags = split_token(w, m - x0)
                if len(frags) > 1:
                    queue = frags + queue
                    continue
                bad.append(w['t'])
            if cur and x0 + wid + add > m:
                placed.append((y, cur))
                y += lead
                cur, wid = [], 0.0
                queue.insert(0, w)      # re-test against the new line's measure
                continue
            cur.append(w)
            wid += add
        if cur:
            placed.append((y, cur))
            y += lead
    return placed, y, bad


def headroom(page, x_lo, x_hi, y_start):
    """How far the right column can rise before it hits something above it."""
    import numpy as np
    dpi = 100
    pix = page.get_pixmap(dpi=dpi)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    g = a[:, :, :3].min(axis=2)
    k = dpi / 25.4
    c0, c1 = int(x_lo * k), int(x_hi * k)
    y = int(y_start * k) - 1
    while y > int(TOP_LIMIT * k):
        if not (g[y, c0:c1] > 246).all():
            break
        y -= 1
    return max(0.0, y_start - (y + 1) / k)


