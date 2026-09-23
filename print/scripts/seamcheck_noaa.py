import sys, pymupdf
pymupdf.TOOLS.set_aa_level(0)          # render the way a RIP does: no edge smoothing
sys.argv = [sys.argv[0]] + sys.argv[1:]
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seamcheck.py'), encoding='utf-8').read())
