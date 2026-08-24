# Postcards landing pages

QR-code landing pages for the University of Cambridge Language Centre A5
postcards. Each page is the destination of the QR code printed on one card
side, so a visitor arrives on the page matching the card in their hand.

## Stack

- HTML5 + native web components (light DOM, no framework)
- Tailwind CSS v4
- Vite
- Bun scripts

## Pages

| Page | Postcard |
| --- | --- |
| `index.html` | reference index of all pages |
| `english-conversation-hours.html` | English Intermediate & Advanced Conversation Hours |
| `intermediate-conversation-hours.html` | French, German & Spanish Intermediate |
| `advanced-conversation-hours.html` | French, German & Spanish Advanced |
| `portuguese-conversation-hours.html` | Portuguese Intermediate & Advanced |
| `friends-without-frontiers.html` | Friends Without Frontiers |
| `conversation-exchange.html` | Conversation Exchange |
| `language-advising.html` | Language Advising |
| `study-abroad.html` | Study Abroad |
| `visit-our-study-centre.html` | Visit our Study Centre |

## Run

```bash
bun install
bun run dev      # dev server
bun run build    # production build into dist/
```

Adding a page means adding an entry to `vite.config.js` as well as the HTML
file — the pages are intentionally separate entry points.

## Design system

The 2026 redesign follows the printed cards. Everything page-specific is a
CSS custom property; everything else is a Tailwind utility in the markup.

- **Palette** — `src/styles/main.css` `@theme`. Teals sampled directly from
  the print PDFs, exposed as Tailwind tokens (`bg-teal-600`, `text-ink`, …).
- **Themes** — one `.theme-*` class per card side, set on `<body>`. Each
  only overrides `--band` (the three header gradient stops), `--color-footer`,
  `--color-accent` and `--color-notch`. Nothing else varies per page.
- **Print motifs** — the things utilities can't express live as `@utility`
  rules: `band-wash` (the header artwork), `band-plate` (the darkening panel
  behind the wordmark), `dot-field`, and `notch` (the footer triangle).
- **Layout** — 60/40 columns, as printed: the title and illustration on the
  left, the copy, fee panel and call to action on the right.
- **Prose** — page bodies are authored as plain HTML. `.card-body` styles
  them by element, with the resets wrapped in `:where()` so the vertical
  rhythm rule at the end of the block still wins.

## Components

`src/scripts/components.js` — light DOM only, no shadow DOM, no dependencies.

| Element | Purpose |
| --- | --- |
| `<lc-header>` | Skip link + diagonal teal banner with the wordmark |
| `<lc-hero-poster>` | Illustration stage (dot field, diagonal wash) |
| `<lc-info-card>` | Heading, lede, and authored body content |
| `<lc-fees>` | The shared fee table (identical on every Conversation Hours card) |
| `<lc-footer>` | Teal footer band, notch, socials, contact details |

`<lc-info-card>` uses the light-DOM slot pattern: it captures `innerHTML`
before overwriting it, so page content stays readable in the HTML source.

## Header band textures

Each card has a Cambridge "expressive" texture full-bleed behind it; the header
band is the top slice. `scripts/build-band-textures.py` cuts that slice from the
designer's artwork into `public/assets/bands/<page>.webp` (10 files, 76 KB all
told — flat gradients compress well).

Two things the script exists to handle:

- Eight of the ten supplied textures are **CMYK print JPEGs** tagged Coated
  FOGRA39. Browsers cannot render CMYK JPEGs, and a naive channel conversion
  turns the brand teal **green**, so each is converted to sRGB through its
  embedded profile.
- It reports the luminance of each band's left and right edge, which is what
  sets `--band-plate` and `--color-band` per theme. Several bands are mid-tone,
  where neither white nor ink clears WCAG AA on its own, so those get a
  darkening plate behind the reversed wordmark; bands that are already dark set
  `--band-plate: 0`. The URL takes ink on pale bands and white on dark ones.

Re-run it after the designer supplies new artwork:

```bash
pip install pillow
python scripts/build-band-textures.py
```

Footers stay on the flat theme teal. The printed footers are the bottom slice of
the same texture, but several run dark on one side and pale on the other, so no
single text colour clears AA across them.

The **dot field** is built in CSS, not shipped as an image: a
`radial-gradient` at the printed pitch and dot size (11pt pitch, 3.3pt dot on a
420pt card, scaled to the content column) in the sampled `--color-dot`, with a
45-degree `mask-image` fading it out towards the bottom right.

## Assets

- `public/assets/illustrations/` — the designer's line drawings, as supplied
  in the 2026 asset pack, renamed to kebab-case.
- `public/assets/bands/` — generated; see above.
- Superseded 2025 placeholder artwork is kept in `old_files/assets-2025/`.
- The designer's source PDFs and asset archive live in `design/`, which is
  gitignored — ask the design team for a copy.

## Typography

- **Feijoa** for headlines and quotes, used sparingly — page `h1`s and the
  index card titles, nothing else.
- **Open Sans** for everything read at length.
- Nothing on screen is below **16px**; long-form text runs at **150%** line
  height. Both come from the `--text-body` / `--leading-body` tokens, so
  prose sizing changes in one place.

Feijoa ships Medium (500) and Bold (700) only — **there is no 600 weight**, so
display type must use `font-medium` or `font-bold`, never `font-semibold`.
Open Sans has 400/600/700, so `font-semibold` is fine on body text.

### Webfonts

Both families are self-hosted from `public/fonts/`, so there is no
third-party font request. Only `.woff2` is served (~352 KB for all six
faces). The licensed OTF/TTF originals live in `fonts-src/`, outside the
served directory, so they are not copied into every deploy.

After adding or replacing an original in `fonts-src/`, regenerate the served
woff2:

```bash
pip install fonttools brotli
python -c "
from fontTools.ttLib import TTFont
import glob, os
for f in glob.glob('fonts-src/*.[ot]tf'):
    t = TTFont(f); t.flavor = 'woff2'
    t.save('public/fonts/' + os.path.splitext(os.path.basename(f))[0] + '.woff2')
"
```

Then add a matching `@font-face` rule in `src/styles/main.css`. The two faces
needed for first paint (`OpenSans-Regular`, `Feijoa-Bold`) are preloaded from
each page's `<head>`.

## Notes

- Cookie consent is CookieControl; the config in `src/scripts/cookies.js` is
  imported by `main.js` so Vite bundles it. Loading it as a separate classic
  `<script src="./src/…">` breaks the production build.
- The cookie widget injects its own `<h1>`; that is why a page reports two.
