"""v5 postcards: v4 + 1.2x leading, wider right column, new short links,
the card's short link beside its QR code, and the LC logo top right.

Column: the left edge moves left to 5mm clear of the heading/illustration (never
right of where the designer put it). Leading is 1.2x the type size; if a side
will not fit it steps down to 1.15x, then 1.1x, and says so.
"""
import glob, os
import numpy as np
import pymupdf

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textlib.py'), encoding='utf-8').read())
from qrlogo import draw_qr, LONG
from svglogo import logo_pdf
from heroscale import scale_hero

OUTDIR = paths.CARDS
os.makedirs(OUTDIR, exist_ok=True)
LOGOS = paths.LOGOS
LOGO_DARK = logo_pdf(os.path.join(LOGOS, 'LC_logo_Black_LightMode_SVG.svg'))
LOGO_LIGHT = logo_pdf(os.path.join(LOGOS, 'LC_logo_White_DarkMode_SVG.svg'))

LEADS = tuple(float(x) for x in os.environ.get('LEADS', '1.2,1.15,1.1').split(','))
BODY_SIZE = float(os.environ.get('BODY_SIZE', '0'))   # 0 = keep the designer's size
ART_GUTTER = 5.0                 # column clearance from the heading/illustration
LABEL_SIZE = 8.0
LABEL_GAP = 2.5                  # label to QR
LOGO_H = float(os.environ.get('LOGO_H', '9'))   # header logo height
LOCKUP_CY = (6.94 + 13.63) / 2   # vertical centre of the University lockup's ink
LOGO_CY = LOCKUP_CY
LOGO_RIGHT = 148.0 - 6.94        # mirrors the lockup's 6.94mm left margin
URL_OPTICAL = 0.38               # URL's optical centre sits this many ems above its baseline
URL_GAP = 3.5

BOOKING = 'bit.ly/4xKLM9h'       # www.langcen.cam.ac.uk/advising/speaking-practice
MOODLE = 'bit.ly/4htBwMy'        # www.vle.cam.ac.uk/course/view.php?id=67022

# descender/ascender of Open Sans as a fraction of the size
ASC, DESC = 1.069, 0.293
LINE_H = ASC + DESC


KEEP_TOP = QR_Y0 - TOP_PAD
LAB_X = QR_X0                    # left edge of the short-link label (set per side)


def measure(y, lead):
    """Right limit for a line at y: clear of the code, and above it clear of just the label."""
    if y > QR_BOTTOM or y + lead < KEEP_TOP:
        return FULL_RIGHT
    if y + lead < QR_Y0 - TOP_PAD:
        return QR_X0 - GUTTER                  # label band: stay clear of the code's column so the link reads as the code's
    return QR_X0 - GUTTER


def to_words(chars, short):
    words, cur = [], []
    for ch, sp in list(chars) + [(' ', None)]:
        if ch.isspace():
            if cur:
                words.append(dict(t=''.join(c for c, _ in cur), sp=cur[0][1]))
                cur = []
        else:
            cur.append((ch, sp))
    glued, i = [], 0
    while i < len(words):
        if words[i]['t'] in ('•', '·', '-') and i + 1 < len(words):
            nxt = words[i + 1]
            glued.append(dict(t=words[i]['t'] + ' ' + nxt['t'], sp=nxt['sp']))
            i += 2
        else:
            glued.append(words[i])
            i += 1
    # keep a short bracketed phrase, e.g. "(outside of term)", together
    joined, i = [], 0
    while i < len(glued):
        w = glued[i]
        if w['t'].startswith('(') and ')' not in w['t']:
            j = i + 1
            while j < len(glued) and j - i < 4 and ')' not in glued[j]['t']:
                j += 1
            if j < len(glued) and ')' in glued[j]['t']:
                joined.append(dict(t=' '.join(x['t'] for x in glued[i:j + 1]), sp=w['sp']))
                i = j + 1
                continue
        joined.append(w)
        i += 1
    glued = joined
    # keep a UK postcode (e.g. CB2 3EL) on one line
    import re
    kept, i = [], 0
    while i < len(glued):
        if (i + 1 < len(glued) and re.fullmatch(r'[A-Z]{1,2}\d[A-Z\d]?', glued[i]['t'])
                and re.fullmatch(r'\d[A-Z]{2}[.,]?', glued[i + 1]['t'])):
            kept.append(dict(t=glued[i]['t'] + ' ' + glued[i + 1]['t'], sp=glued[i]['sp']))
            i += 2
        else:
            kept.append(glued[i])
            i += 1
    words, subs = kept, []
    for w in words:
        low = w['t'].lower().rstrip('.')
        dot = '.' if w['t'].endswith('.') else ''
        if 'langcen.cam.ac.uk/advising/speaking-practice' in low or low == 'www.langcen.cam.ac.uk/':
            subs.append((w['t'], BOOKING + dot))
            w['t'] = BOOKING + dot
        elif 'vle.cam.ac.uk' in low:
            subs.append((w['t'], MOODLE + dot))
            w['t'] = MOODLE + dot
    return words, subs


BULLETS = ('•', '·', '-')

# Wording changes requested for the print run: (side, keep text up to and including this phrase,
# or drop the whole line when it contains the phrase)
TRUNCATE_AFTER = {('LanguageAdvising_StudyAbroad', 1): ['Explore your options by booking a study abroad']}
DROP_LINES = {('LanguageAdvising_StudyAbroad', 1): ['vle.cam.ac.uk']}
REPLACE = {('FriendsWithoutFrontiers_Conversation Exchange', 0): [('20- or 30-minute', '20 or 30-minute')],
           ('EnglishConversationHours_VisitOurStudyCentre', 1): [('(outside of term)', '(outside term)')],
           ('PortugueseConversationHoursIntermediateAndAdvanced_VisitOurStudyCentre', 1): [('(outside of term)', '(outside term)')]}
# footer email replacements: (side) -> (old, new); right edge and baseline kept
FOOTER_EMAIL = {('FriendsWithoutFrontiers_Conversation Exchange', 1):
                ('enquiries@langcen.cam.ac.uk', 'conversation@langcen.cam.ac.uk')}


def apply_edits(lines, key):
    out = []
    for ln in lines:
        t = ''.join(c for c, _ in ln)
        if any(p in t for p in DROP_LINES.get(key, [])):
            continue
        for p in TRUNCATE_AFTER.get(key, []):
            if p in t:
                ln = ln[:t.index(p) + len(p)]
        for old, new in REPLACE.get(key, []):
            t = ''.join(c for c, _ in ln)
            if old in t:
                i = t.index(old)
                ln = ln[:i] + [(c, ln[i][1]) for c in new] + ln[i + len(old):]
        out.append(ln)
    return out


def merge_soft(lines):
    """Rejoin lines the designer's narrow measure wrapped, so the wider column is
    used. A break is kept after ':' '.' '!' '?', before a bullet, and between
    different weights (bold heading / regular body). Joined when the next line
    starts lower-case (a sentence carrying on) or this line ends with a comma
    (address parts, lists in prose)."""
    def txt(l):
        return ''.join(c for c, _ in l)

    out = []
    for ln in lines:
        if out:
            prev = out[-1]
            a, b = txt(prev).rstrip(), txt(ln).strip()
            same_weight = prev[-1][1]['font'] == ln[0][1]['font'] if prev and ln else False
            if (a and b and same_weight and b[0] not in BULLETS
                    and a[-1] not in ':.!?'
                    and (b[0].islower() or a[-1] == ',')):
                sp = prev[-1][1]
                out[-1] = [(c, s) for c, s in prev if True] + ([(' ', sp)] if not txt(prev).endswith(' ') else []) + list(ln)
                continue
        out.append(list(ln))
    return out


def lum(rgb255):
    c = [x / 255.0 for x in rgb255]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(l1, l2):
    a, b = sorted((l1, l2))
    return (b + 0.05) / (a + 0.05)


def art_right(page, col_x):
    """Right edge (mm) of the heading/illustration ink left of the column."""
    k = 100 / 25.4
    pix = page.get_pixmap(dpi=100)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    band = a[int(24 * k):int(88 * k), :int((col_x - 0.3) * k)]
    c = np.where((band.min(axis=2) < 200).any(axis=0))[0]
    return c.max() / k if len(c) else 0.0


LEFT_BOTTOM = 88.6               # Visit sides: bottom of the moved address block (rule at 90.06)
HERO_GAP = 3.0                   # between the scaled illustration and the address block


def visit_left_layout(path, doc, pno, visit_left, heading_spans):
    """Visit sides: address and 'Contact us' go under the illustration, left-aligned with
    the heading and bottom-aligned above the rule; the email (repeated in the footer) is
    dropped and the phone joins 'Contact us:' on one line. The illustration is scaled to
    fit above, keeping its top edge and horizontal centre."""
    addr = [b for b in visit_left if 'Language Centre' in ''.join(s['text'] for l in b['lines'] for s in l['spans'])][0]
    cont = [b for b in visit_left if 'Contact us' in ''.join(s['text'] for l in b['lines'] for s in l['spans'])][0]
    x0 = min(sp['bbox'][0] for sp in heading_spans) / PT
    lines = []
    for chars in merge_soft(raw_lines(addr)):
        t = ''.join(c for c, _ in chars).strip()
        lines.append((t, chars[0][1]))
    c_sp = cont['lines'][0]['spans'][0]
    phone = [''.join(s['text'] for s in l['spans']).strip() for l in cont['lines']
             if any(ch.isdigit() for ch in ''.join(s['text'] for s in l['spans']))][0]
    phone = phone.lstrip('•· ').strip()
    phone_sp = [l['spans'][-1] for l in cont['lines'] if phone in ''.join(s['text'] for s in l['spans'])][0]
    size = c_sp['size']
    lead = 1.2 * size / PT
    gap = max(1.5, cont['bbox'][1] / PT - addr['bbox'][3] / PT)
    # bottom-up: contact line, then the address lines
    base_contact = LEFT_BOTTOM - DESC * size / PT
    out = []
    lab = 'Contact us:'
    out.append((x0, base_contact, lab, c_sp))
    fw = font_for(c_sp['font'])[0].text_length(lab + ' ', size) / PT
    out.append((x0 + fw, base_contact, phone, phone_sp))
    y = base_contact - (LINE_H * size / PT) - gap
    for t, sp in reversed(lines):
        out.append((x0, y, t, sp))
        y -= lead
    top_ink = y + lead - ASC * size / PT
    widest = max(font_for(sp['font'])[0].text_length(t, sp['size']) / PT for _, _, t, sp in out[2:])
    # scale the illustration to sit above
    from herorun import hero_run
    box = hero_run(path, pno)['box']
    target = top_ink - HERO_GAP
    factor = min(1.0, (target - box[1]) / (box[3] - box[1]))
    factor = min(factor, float(os.environ.get('VISIT_FACTOR', '0.66')))   # same size on both Visit cards   # same size on both Visit cards
    anchor = ((box[0] + box[2]) / 2, box[1])
    ob, nb = scale_hero(path, doc, pno, factor, anchor)
    note = ('          Visit layout: illustration scaled to %.0f%% (%.1f x %.1f mm -> %.1f x %.1f mm); address + contact moved under it at x %.1f, '
            'y %.1f-%.1f, widest line %.1f mm; email dropped (it is in the footer)'
            % (factor * 100, ob[2] - ob[0], ob[3] - ob[1], nb[2] - nb[0], nb[3] - nb[1], x0, top_ink, LEFT_BOTTOM, widest))
    return out, factor, anchor, note


def build(path):
    stem = os.path.basename(path).replace('_A5_v2.pdf', '')
    doc = pymupdf.open(path)
    notes, problems = [], []
    for pno, page in enumerate(doc):
        short = SHORT[(stem, pno)]
        blocks, subs_all = [], []
        heading_spans = [sp_ for b_ in page.get_text('dict')['blocks'] if b_['type'] == 0
                         for l_ in b_['lines'] for sp_ in l_['spans']
                         if 'Feijoa' in sp_['font'] and sp_['bbox'][0] / PT < COL_X]
        visit = any('Visit our Study Centre' in sp_['text'] for sp_ in heading_spans)
        visit_left = []          # Visit sides: address + contact move under the illustration
        dropped = []             # blocks emptied by requested wording changes
        for b in page.get_text('dict')['blocks']:
            if b['type'] != 0:
                continue
            if visit and b['bbox'][0] / PT >= COL_X:
                t_ = ''.join(sp_['text'] for l_ in b['lines'] for sp_ in l_['spans']).strip()
                if t_.startswith('Language Centre,') or t_.startswith('Contact us'):
                    visit_left.append(b)
                    continue
            if b['bbox'][0] / PT < COL_X:
                # some blocks hold the left heading AND the column's first lines;
                # take just the lines that sit in the column
                sub = [l for l in b['lines'] if l['bbox'][0] / PT >= COL_X
                       and TOP_LIMIT <= l['bbox'][1] / PT <= BOTTOM_LIMIT]
                if not sub:
                    continue
                r = pymupdf.Rect(sub[0]['bbox'])
                for l in sub[1:]:
                    r |= pymupdf.Rect(l['bbox'])
                b = dict(b, lines=sub, bbox=tuple(r))
            x0, y0, x1, y1 = [v / PT for v in b['bbox']]
            if x0 < COL_X or y0 < TOP_LIMIT or y0 > BOTTOM_LIMIT:
                continue
            lns = b['lines']
            if BODY_SIZE:
                for l_ in lns:
                    for s_ in l_['spans']:
                        s_['size'] = BODY_SIZE
            logical = []
            for chars in apply_edits(merge_soft(merge_midtoken(raw_lines(b))), (stem, pno)):
                ws, sb = to_words(chars, short)
                subs_all += sb
                if ws:
                    logical.append(ws)
            if not logical:
                dropped.append(b)
                continue
            blocks.append(dict(b=b, x0=x0, y0=y0, y1=y1, logical=logical,
                               size=lns[0]['spans'][0]['size'], nlines=len(lns),
                               color=lns[0]['spans'][0]['color']))
        blocks.sort(key=lambda z: z['y0'])
        body_color = blocks[-1]['color'] if blocks else 0x101f2a

        left_lines = []
        if visit:
            left_lines, factor, anchor, hero_note = visit_left_layout(path, doc, pno, visit_left, heading_spans)
            notes.append(hero_note)

        # --- column geometry --------------------------------------------------
        col0 = min(b_['x0'] for b_ in blocks)
        head_right = max((sp_['bbox'][2] / PT for b_ in page.get_text('dict')['blocks'] if b_['type'] == 0
                          for l_ in b_['lines'] for sp_ in l_['spans']
                          if 'Feijoa' in sp_['font'] and sp_['bbox'][0] / PT < COL_X), default=0.0)
        if os.environ.get('HERO_FREE'):
            # test mode: pretend the illustration is out of the way; only the heading limits the column
            new_col = round(head_right + ART_GUTTER, 1)
        else:
            new_col = min(col0, round(art_right(page, col0) + ART_GUTTER, 1))
        shift = col0 - new_col

        # label beside the QR: its top bounds the text column
        lab_font, lab_path, lab_base = font_for('OpenSans-SemiBold')
        label = 'bit.ly/' + short
        lab_w = lab_font.text_length(label, LABEL_SIZE) / PT
        global KEEP_TOP, LAB_X
        if os.environ.get('LABEL_POS', 'above') == 'above':
            # right-aligned over the code; only the narrow QR column pays for it
            lab_base_y = QR_Y0 - 2.0 - DESC * LABEL_SIZE / PT     # 2 mm clear: outside the code's 1.6 mm quiet zone
            lab_top = lab_base_y - ASC * LABEL_SIZE / PT
            lab_x = min(QR_X0 + (QR_SIZE - lab_w) / 2, QR_RIGHT + 0.5 - lab_w)   # centred over the code
            KEEP_TOP = lab_top - 1.0
            LAB_X = lab_x
            text_bottom = BOTTOM_LIMIT
        else:
            lab_base_y = QR_BOTTOM - DESC * LABEL_SIZE / PT
            lab_top = lab_base_y - ASC * LABEL_SIZE / PT
            lab_x = QR_X0 - LABEL_GAP - lab_w
            KEEP_TOP = QR_Y0 - TOP_PAD
            LAB_X = QR_X0
            text_bottom = lab_top - 1.2

        gaps = [blocks[i + 1]['y0'] - blocks[i]['y1'] for i in range(len(blocks) - 1)]
        if visit and os.environ.get('VISIT_HOURS') == 'gaps':
            gaps = [g * float(os.environ.get('VISIT_GAP', '0.55')) for g in gaps]   # option B

        def layout(start, lf):
            y, out, bad = start, [], []
            for i, blk in enumerate(blocks):
                lead = lf * blk['size'] / PT
                lines, _, b2 = lay_block(blk['logical'], blk['x0'] - shift, y, lead)
                bad += b2
                vis_bottom = (lines[-1][0] if lines else y) + LINE_H * blk['size'] / PT
                out.append((blk, lines, vis_bottom, lead))
                if i < len(gaps):
                    y = vis_bottom + gaps[i]
            return out, bad

        top0 = blocks[0]['y0']
        room = headroom(page, new_col, FULL_RIGHT, top0)
        # keep the column's top aligned with the heading: lift at most to 1.5mm above it
        head_top = min((sp_['bbox'][1] / PT for sp_ in heading_spans), default=top0)
        full_room = room
        room = max(0.0, min(room, top0 - (head_top - 1.5)))
        chosen = None
        # try each spacing first within the heading-aligned lift, then (only if needed to keep
        # that spacing) with all the free space above the column
        tries = []
        visit_mode = os.environ.get('VISIT_HOURS', '') if visit else ''
        for lf in LEADS:
            if visit_mode == 'lift':
                tries += [(lf, full_room)]          # option A: lift past the heading line to keep the hours whole
            else:
                tries += [(lf, room), (lf, full_room)] if full_room > room else [(lf, room)]
        for lf, lim in tries:
            # of the lifts that fit, take the one with the fewest lines (fewest forced breaks),
            # then the smallest lift
            best = None
            for lift in np.arange(0.0, lim + 0.001, 0.25):
                placed, bad = layout(top0 - lift, lf)
                if not bad and placed[-1][2] <= text_bottom:
                    nl = sum(len(l_) for _, l_, _, _ in placed)
                    if best is None or nl < best[0]:
                        best = (nl, lift, placed)
            if best:
                chosen = (lf, best[1], best[2])
                break
        if not chosen:
            lf, lift = LEADS[-1], room
            placed, bad = layout(top0 - lift, lf)
            over = placed[-1][2] - text_bottom
            problems.append((pno + 1, 'column too long by %.1fmm even at %.2fx' % (over, lf)))
            chosen = (lf, lift, placed)
        lf, lift, placed = chosen
        grew = sum(1 for blk, lines, _, _ in placed if len(lines) != blk['nlines'])
        notes.append('    p%d  column %.1f -> %.1fmm (width %.1f -> %.1f)  leading %.2fx  lifted %.1f of %.1fmm  %d block(s) re-wrapped  bottom %.1f / %.1f'
                     % (pno + 1, col0, new_col, FULL_RIGHT - col0, FULL_RIGHT - new_col, lf, lift, room, grew,
                        placed[-1][2], text_bottom))
        for a_, b_ in subs_all:
            notes.append('          link  %s  ->  %s' % (a_, b_))

        # --- header: move the URL left, add the logo --------------------------
        hdr = [b for b in page.get_text('dict')['blocks'] if b['type'] == 0 and b['bbox'][3] / PT < 20
               and 'www.langcen' in ''.join(s['text'] for l in b['lines'] for s in l['spans'])][0]
        usp = hdr['lines'][0]['spans'][0]

        # --- redact and re-set ------------------------------------------------
        for blk, lines, _, _ in placed:
            r = pymupdf.Rect(blk['b']['bbox'])
            r.y0 -= 2.0
            r.y1 += 2.0
            r.x1 = min(r.x1 + 5.0, 148 * PT)
            page.add_redact_annot(r)
        for b_ in visit_left + dropped:
            r = pymupdf.Rect(b_['bbox'])
            r.y0 -= 1.0
            r.y1 += 1.0
            r.x1 = min(r.x1 + 5.0, 148 * PT)
            page.add_redact_annot(r)
        foot = []
        if (stem, pno) in FOOTER_EMAIL:
            old_e, new_e = FOOTER_EMAIL[(stem, pno)]
            foot = [sp_ for b_ in page.get_text('dict')['blocks'] if b_['type'] == 0 for l_ in b_['lines']
                    for sp_ in l_['spans'] if sp_['text'].strip() == old_e and sp_['bbox'][1] / PT > 89]
            assert len(foot) == 1, 'footer email not found once'
            page.add_redact_annot(pymupdf.Rect(foot[0]['bbox']))
        page.add_redact_annot(pymupdf.Rect(hdr['bbox']))
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)

        for blk, lines, _, _ in placed:
            asc = blk['size'] * 0.75 / PT
            for y, ws in lines:
                x = blk['x0'] - shift
                for i, w in enumerate(ws):
                    f, fpath, fbase = font_for(w['sp']['font'])
                    if i and not w.get('nosp'):
                        x += wspace(w)
                    page.insert_text(pymupdf.Point(x * PT, (y + asc) * PT), w['t'],
                                     fontsize=w['sp']['size'], fontfile=fpath,
                                     fontname=fbase, color=rgb(w['sp']['color']))
                    x += wtext(w)

        for x_, base_, t_, sp_ in left_lines:
            f, fpath, fbase = font_for(sp_['font'])
            page.insert_text(pymupdf.Point(x_ * PT, base_ * PT), t_, fontsize=sp_['size'],
                             fontfile=fpath, fontname=fbase, color=rgb(sp_['color']))

        for sp_ in foot:
            new_e = FOOTER_EMAIL[(stem, pno)][1]
            f, fpath, fbase = font_for(sp_['font'])
            w_ = f.text_length(new_e, sp_['size'])
            page.insert_text(pymupdf.Point(sp_['bbox'][2] - w_, sp_['origin'][1]), new_e, fontsize=sp_['size'],
                             fontfile=fpath, fontname=fbase, color=rgb(sp_['color']))
            notes.append('          footer email %s -> %s (right-aligned at %.1fmm)' % (sp_['text'].strip(), new_e, sp_['bbox'][2] / PT))

        # logo colour from measured contrast against the header behind it
        lr = LOGO_DARK[0].rect
        lw = LOGO_H * lr.width / lr.height
        lrect = pymupdf.Rect((LOGO_RIGHT - lw) * PT, (LOGO_CY - LOGO_H / 2) * PT,
                             LOGO_RIGHT * PT, (LOGO_CY + LOGO_H / 2) * PT)
        pix = page.get_pixmap(dpi=150, clip=lrect)
        px = np.frombuffer(pix.samples, np.uint8).reshape(-1, pix.n)[:, :3]
        ls = np.array([lum(c) for c in px[::3]])
        worst = {'black': min(contrast(0.0012, l) for l in (ls.min(), ls.max())),
                 'white': min(contrast(1.0, l) for l in (ls.min(), ls.max()))}
        pick = max(worst, key=worst.get)
        header_swap = stem.startswith('FriendsWithoutFrontiers') and pno == 0   # FGS header supplies URL + logo
        if not header_swap:
            page.show_pdf_page(lrect, LOGO_DARK if pick == 'black' else LOGO_LIGHT, 0, overlay=True)
        uf, upath, ubase = font_for(usp['font'])
        uw = uf.text_length(usp['text'], usp['size']) / PT
        ux = LOGO_RIGHT - lw - URL_GAP - uw
        u_base = LOCKUP_CY + URL_OPTICAL * usp['size'] / PT      # centre the URL on the lockup
        if not header_swap:
          page.insert_text(pymupdf.Point(ux * PT, u_base * PT), usp['text'], fontsize=usp['size'],
                         fontfile=upath, fontname=ubase, color=rgb(usp['color']))
        notes.append('          header logo %s (worst-case contrast %.1f:1; the other option %.1f:1), URL text #%06x'
                     % (pick, worst[pick], min(worst.values()), usp['color']))
        if worst[pick] < 3.0:
            problems.append((pno + 1, 'header logo contrast only %.1f:1' % worst[pick]))

        # --- QR and its short link --------------------------------------------
        info = draw_qr(page, LONG[short], QR_X0, QR_Y0, QR_SIZE, clear=15)
        page.insert_text(pymupdf.Point(lab_x * PT, lab_base_y * PT), label, fontsize=LABEL_SIZE,
                         fontfile=lab_path, fontname=lab_base, color=rgb(body_color))
        notes.append('          QR -> %s  label %s at x %.1f-%.1f' % (LONG[short], label, lab_x, lab_x + lab_w))

        # Friends Without Frontiers p1: the supplied header carries leftover layers (a flat teal
        # block and a stray image patch); use the FGS Intermediate header background instead.
        if stem.startswith('FriendsWithoutFrontiers') and pno == 0:
            fgs = glob.glob(os.path.join(OUTDIR, 'FrenchGermanAndSpanish*_%s_QR20.pdf' % paths.VERSION))[0]
            hdr_rect = pymupdf.Rect(0, 0, 148 * PT, 22.40 * PT)
            page.show_pdf_page(hdr_rect, pymupdf.open(fgs), 0, clip=hdr_rect, overlay=True)
            notes.append('          header replaced with the FGS Intermediate header (logo, URL and lockup identical)')

        # The University lockup (crest + wordmark) is printed in Pantone spot inks with overprint and a
        # blend mode. Redaction rewrites the page's content and some viewers (pdfium: Chrome/Edge) then
        # show the spot colours wrongly - the crest shifts and one lockup turns yellow. Nothing we edit is
        # in this area, so lay the designer's untouched lockup back over it.
        lock_src = (glob.glob(os.path.join(D, 'FrenchGermanAndSpanish*.pdf'))[0], 0)             if (stem.startswith('FriendsWithoutFrontiers') and pno == 0) else (path, pno)
        lock_rect = pymupdf.Rect(0, 0, 62 * PT, 22.40 * PT)
        page.show_pdf_page(lock_rect, pymupdf.open(lock_src[0]), lock_src[1], clip=lock_rect, overlay=True)

    out = os.path.join(OUTDIR, os.path.basename(path).replace('_v2.pdf', '_%s_QR20.pdf' % paths.VERSION))
    doc.save(out, garbage=4, deflate=True)
    print('\n=== %s' % stem[:62])
    for x in notes:
        print(x)
    return problems


if __name__ == '__main__':
    allp = {}
    for f in sorted(glob.glob(os.path.join(D, '*.pdf'))):
        p = build(f)
        if p:
            allp[os.path.basename(f)] = p
    print('\n--- sides needing attention ---')
    if not allp:
        print('  none')
    for k, v in allp.items():
        print('  %s' % k[:60])
        for item in v:
            print('     p%s  %s' % item)
