import sys, pymupdf, numpy as np
PT = 72/25.4; SL = 9.0; DPI = 1200
d = pymupdf.open(sys.argv[1]); worst = 0
for i, p in enumerate(d):
    for edge in ('L', 'R', 'T', 'B'):
        # a strip 1.2mm either side of the trim along the whole edge
        if edge in 'LR':
            x = SL if edge == 'L' else SL + 148
            clip = pymupdf.Rect((x-1.2)*PT, (SL+1)*PT, (x+1.2)*PT, (SL+104)*PT)
        else:
            y = SL if edge == 'T' else SL + 105
            clip = pymupdf.Rect((SL+1)*PT, (y-1.2)*PT, (SL+147)*PT, (y+1.2)*PT)
        pix = p.get_pixmap(dpi=300, clip=clip)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)
        prof = a.mean(axis=0 if edge in 'TB' else 1) if False else None
        # per position along the edge: max jump between neighbouring pixels across the trim
        ax = 1 if edge in 'LR' else 0
        diff = np.abs(np.diff(a, axis=ax)).max(axis=2)
        c = diff.shape[ax] // 2
        at = diff.take(range(c-2, c+2), axis=ax).max(axis=ax)       # jumps right at the trim
        away = np.concatenate([diff.take(range(0, c-4), axis=ax), diff.take(range(c+4, diff.shape[ax]), axis=ax)], axis=ax).max(axis=ax)
        excess = np.maximum(at - away, 0)
        s = int(np.percentile(excess, 99)); worst = max(worst, s)
        if s > 12: print('  p%d %s edge: seam-like jump %d at the trim' % (i+1, edge, s))
print('worst excess jump at trim across all edges: %d (0-255; under ~12 is invisible)' % worst)
