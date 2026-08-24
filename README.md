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
- **Print motifs** — the four things utilities can't express live as
  `@utility` rules: `band-wash` (diagonal header gradient), `band-plate`
  (angled panel behind the wordmark), `dot-field`, `stage-wash` and `notch`
  (the triangle on the footer edge).
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

## Assets

- `public/assets/illustrations/` — the designer's line drawings, as supplied
  in the 2026 asset pack, renamed to kebab-case.
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
