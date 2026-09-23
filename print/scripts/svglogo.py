"""Load an Illustrator SVG logo as a vector PDF, honouring its <style> classes.

MuPDF ignores CSS in <style>, so each class's fill is written onto its shapes first.
"""
import re
import pymupdf

def logo_pdf(path):
    s = open(path, encoding='utf-8').read()
    css = dict(re.findall(r'\.(st\d+)\s*\{\s*fill:\s*([^;]+);', s))
    for cls, fill in css.items():
        s = s.replace('class="%s"' % cls, 'fill="%s"' % fill.strip())
    doc = pymupdf.open('pdf', pymupdf.open(stream=s.encode('utf-8'), filetype='svg').convert_to_pdf())
    # near-black fills become 100% K (single ink) so they print crisp, not as four-colour rich black
    for x in range(1, doc.xref_length()):
        if doc.xref_is_stream(x):
            t = doc.xref_stream(x)
            t2 = re.sub(rb'(?<![\d.])(0?\.00[0-9]+|0) (0?\.00[0-9]+|0) (0?\.00[0-9]+|0) rg', b'0 0 0 1 k', t)
            if t2 != t:
                doc.update_stream(x, t2)
    return doc

if __name__ == '__main__':
    import glob, os
    import paths
    for f in glob.glob(os.path.join(paths.LOGOS, '*.svg')):
        d = logo_pdf(f)
        print(f.split('/')[-1], sorted({tuple(round(c, 3) for c in dr['fill']) for dr in d[0].get_drawings() if dr.get('fill')}))
