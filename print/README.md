# Printed postcards

Everything for the **printed** Language Centre postcards lives here. The rest of the
repository is the website: the landing pages the cards' QR codes open.

## What's here

| Folder | Contents |
|---|---|
| `package-v7/` | **What goes to the printer**: `00_Print-specification.pdf` and one PDF per card. A zipped copy, `package-v7.zip`, is built alongside it (not committed). |
| `review/` | The staff review PDF, for checking the wording and testing the QR codes before printing. |
| `source/designer/` | The designer's artwork: one 2-page PDF per card (page 1 front, page 2 back). |
| `source/logos/` | The Language Centre logo (black and white) used in the header and in the QR codes. |
| `scripts/` | The build: turns the designer's artwork into the print files, then checks them. |
| `reports/` | Earlier reports, e.g. the illustration gaps found in the designer's delivery. |
| `build/` | Intermediate files. Git-ignored; rebuilt by the scripts. |

The raw designer delivery (zips, PNG previews, illustration SVGs) is kept locally in the
git-ignored `design/` folder at the repository root.

## The cards

Five double-sided A6 cards (148 × 105 mm, landscape), printed head-to-head:

| Card | Front | Back |
|---|---|---|
| 1 | English Intermediate & Advanced Conversation Hours | Visit our Study Centre |
| 2 | French, German & Spanish Intermediate Conversation Hours | French, German & Spanish Advanced Conversation Hours |
| 3 | Friends Without Frontiers | Conversation Exchange |
| 4 | Language Advising | Study Abroad |
| 5 | Portuguese Intermediate & Advanced Conversation Hours | Visit our Study Centre |

## Rebuilding

```
python print/scripts/make_all.py
```

This rebuilds the cards, the print files, the review PDF and the printer package, then runs
`preflight.py`, which fails the build if any check fails. The checks cover PDF structure,
fonts, image resolution, every QR code (decoded in two PDF engines), the University logo's
colours, the agreed wording, the layout, the bleed and the live links.

Requires Python 3 with `pymupdf`, `pypdfium2`, `pikepdf`, `zxing-cpp`, `opencv-python`,
`numpy`, `Pillow` and `segno`.

## What the build changes, and why

Starting from the designer's files, `build7.py`:

- **Text:** resets the right-hand column at 9 pt with 1.2× line spacing (supplied at 0.9×,
  where lines touched), and widens the column to 5 mm from the illustration.
- **Wording:** applies the agreed edits. Booking and Moodle links became short links, the
  Moodle wording was removed from Study Abroad, "20-" became "20" on Friends Without
  Frontiers, "(outside term)" is used on Visit our Study Centre, and Conversation Exchange
  uses `conversation@langcen.cam.ac.uk`.
- **QR codes:** each is 20 × 20 mm, encodes the full landing-page URL (not bit.ly), has the
  LC logo in the centre, and is 100% black ink. The card's short link sits above the code.
- **Header:** adds the LC logo top right, sharing one centre line with the URL and the
  University lockup.
- **Visit our Study Centre:** the books illustration is scaled to 66%, with the address and
  phone number moved beneath it.
- **Friends Without Frontiers front:** uses the FGS Intermediate header background, because
  the supplied one contained leftover layers.

`bleed7.py` adds a 3 mm bleed by mirroring the artwork at each edge (the designer's export
had no bleed) and adds crop marks outside the bleed.

**Known trap.** The University logo is printed in Pantone spot colours. Editing a page with
MuPDF's redaction tool, or saving with `clean=True`, rewrites the page's drawing
instructions, and Chrome/Edge (pdfium) then show the logo in the wrong colours. The build
lays the designer's untouched logo back over its own area, and never saves with
`clean=True`. `lockcheck.py` and the preflight check this in pdfium.
