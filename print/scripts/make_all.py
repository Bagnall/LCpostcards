"""Rebuild everything for print, then preflight it.

    python print/scripts/make_all.py

1. build7.py     designer PDFs -> edited cards at trim size        (print/build/cards)
2. bleed7.py     cards -> 3 mm mirrored bleed + crop marks          (print/build/print-ready)
3. reviewpack.py cards -> staff review PDF                          (print/review)
4. printpack.py  print-ready -> printer package + spec + zip        (print/package-v7, print/package-v7.zip)
5. preflight.py  checks the package: structure, fonts, images, QR codes (MuPDF + pdfium),
                 University logo colours, wording, layout, bleed, live links
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
for step in ('build7.py', 'bleed7.py', 'reviewpack.py', 'printpack.py', 'preflight.py'):
    print('\n######## %s' % step, flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, step)], cwd=HERE)
    if r.returncode:
        sys.exit('%s failed (exit %d)' % (step, r.returncode))
