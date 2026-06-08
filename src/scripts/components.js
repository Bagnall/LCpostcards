/**
 * LC Postcard Pages — Web Components
 * Light DOM only. No Shadow DOM. No external dependencies.
 * Import this file from src/main.js — Vite will bundle it automatically.
 */

// ---------------------------------------------------------------------------
// Shared helper — prevents XSS when attribute values are interpolated into
// innerHTML. Do NOT apply to trusted authored slot HTML.
// ---------------------------------------------------------------------------
function escapeHTML(str) {
	return String(str ?? '')
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;');
}


// ---------------------------------------------------------------------------
// SVG definitions — centralised so they're easy to update
// ---------------------------------------------------------------------------
const SVG_LC_LOGO = `<svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" viewBox="0 0 595.28 830.54" fill="currentColor">
	<path d="M590.24 617.1c-26.07 31.23-59.48 51.6-94.81 66.01-11.16 4.53-22.64 8.19-34.32 10.89-20.54 4.78-41.7 6.66-62.81 5.56-31.08-1.62-62.1-9.71-91.11-24.6-96.58-49.58-143.25-160.12-114.43-262.79 6.54-23.3 18.38-48.02 32.58-68.33 39.72-56.7 106-92.34 172.58-95.87 18.32-.98 36.1.85 52.74 3.88 11.93 2.17 22.4 4.47 34.14 8.56 39.7 13.77 70.66 36.26 107.11 74.84 1.01 1.25 2.27 2.61 3.36 3.59-1.19-2.3-2.77-4.73-4.02-6.83-54.71-91.92-168.93-132.14-273.39-108.88-55.86 12.45-105.67 42.69-143.31 88.8-35.02 42.87-54.06 92.67-58.6 145.45-1.72 81.75 0 279.24 0 279.24l75.07-76.34c.58.45 1.05 1.22 1.61 1.61 3.6 2.44 7.98 6.71 11.24 9.65 41.26 37.1 91.23 57.87 144.52 63.49 33.96 3.57 67.96.77 98.75-8.04 63.57-18.19 117.55-51.04 146.78-112.26l1.35-3.23c-1.35 1.82-3.02 3.46-5.07 5.66l.03-.03Zm1.55-282.07c-.16-.21-.34-.42-.5-.61-3.51-4.71-7.2-9.29-11.06-13.72-.05-.05-.08-.11-.13-.16 3.91 4.47 7.64 9.09 11.19 13.83.16.21.34.43.51.64h-.02v.02ZM127.13 334.11c.5-.42 1.01-.82 1.51-1.24-.5.42-1.01.82-1.51 1.24" class="st0"/>
	<path d="M200.24 288.33c.63-.29 1.25-.56 1.88-.84-.63.27-1.25.55-1.88.84" class="st0"/>
	<ellipse cx="312.34" cy="476.44" class="st0" rx="28.46" ry="28.48"/>
	<ellipse cx="399.17" cy="476.44" class="st0" rx="28.46" ry="28.48"/>
	<ellipse cx="486.01" cy="476.44" class="st0" rx="28.46" ry="28.48"/>
	<path d="M85.45 720.56V415.27h.03V0H.14v462.9c-.1 3.14-.14 6.29-.14 9.46 0 2.12.03 4.25.08 6.37-.03 1.62-.08 3.25-.08 4.89 0 2.43.03 4.84.08 7.25-.05 2.27-.08 4.55-.08 6.82 0 85.69 32.32 163.81 85.45 222.88ZM237.01 731.13c-15.82-8.12-30.52-17.58-44.13-28.13l-60.82 61.64c50.72 38.01 112.61 61.94 179.9 65.9v-73.52c-25.62-4.95-50.85-13.54-74.95-25.91z" class="st0"/>
</svg>`;

const SVG_FACEBOOK = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" aria-hidden="true">
	<path d="M576 320C576 178.6 461.4 64 320 64C178.6 64 64 178.6 64 320C64 440 146.7 540.8 258.2 568.5L258.2 398.2L205.4 398.2L205.4 320L258.2 320L258.2 286.3C258.2 199.2 297.6 158.8 383.2 158.8C399.4 158.8 427.4 162 438.9 165.2L438.9 236C432.9 235.4 422.4 235 409.3 235C367.3 235 351.1 250.9 351.1 292.2L351.1 320L434.7 320L420.3 398.2L351 398.2L351 574.1C477.8 558.8 576 450.9 576 320z" fill="#fff"/>
</svg>`;

const SVG_INSTAGRAM = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" aria-hidden="true">
	<path d="M320.3 205C256.8 204.8 205.2 256.2 205 319.7C204.8 383.2 256.2 434.8 319.7 435C383.2 435.2 434.8 383.8 435 320.3C435.2 256.8 383.8 205.2 320.3 205zM319.7 245.4C360.9 245.2 394.4 278.5 394.6 319.7C394.8 360.9 361.5 394.4 320.3 394.6C279.1 394.8 245.6 361.5 245.4 320.3C245.2 279.1 278.5 245.6 319.7 245.4zM413.1 200.3C413.1 185.5 425.1 173.5 439.9 173.5C454.7 173.5 466.7 185.5 466.7 200.3C466.7 215.1 454.7 227.1 439.9 227.1C425.1 227.1 413.1 215.1 413.1 200.3zM542.8 227.5C541.1 191.6 532.9 159.8 506.6 133.6C480.4 107.4 448.6 99.2 412.7 97.4C375.7 95.3 264.8 95.3 227.8 97.4C192 99.1 160.2 107.3 133.9 133.5C107.6 159.7 99.5 191.5 97.7 227.4C95.6 264.4 95.6 375.3 97.7 412.3C99.4 448.2 107.6 480 133.9 506.2C160.2 532.4 191.9 540.6 227.8 542.4C264.8 544.5 375.7 544.5 412.7 542.4C448.6 540.7 480.4 532.5 506.6 506.2C532.8 480 541 448.2 542.8 412.3C544.9 375.3 544.9 264.5 542.8 227.5zM495 452C487.2 471.6 472.1 486.7 452.4 494.6C422.9 506.3 352.9 503.6 320.3 503.6C287.7 503.6 217.6 506.2 188.2 494.6C168.6 486.8 153.5 471.7 145.6 452C133.9 422.5 136.6 352.5 136.6 319.9C136.6 287.3 134 217.2 145.6 187.8C153.4 168.2 168.5 153.1 188.2 145.2C217.7 133.5 287.7 136.2 320.3 136.2C352.9 136.2 423 133.6 452.4 145.2C472 153 487.1 168.1 495 187.8C506.7 217.3 504 287.3 504 319.9C504 352.5 506.7 422.6 495 452z" fill="#fff"/>
</svg>`;

const SVG_LINKEDIN = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" aria-hidden="true">
	<path d="M512 96L127.9 96C110.3 96 96 110.5 96 128.3L96 511.7C96 529.5 110.3 544 127.9 544L512 544C529.6 544 544 529.5 544 511.7L544 128.3C544 110.5 529.6 96 512 96zM231.4 480L165 480L165 266.2L231.5 266.2L231.5 480L231.4 480zM198.2 160C219.5 160 236.7 177.2 236.7 198.5C236.7 219.8 219.5 237 198.2 237C176.9 237 159.7 219.8 159.7 198.5C159.7 177.2 176.9 160 198.2 160zM480.3 480L413.9 480L413.9 376C413.9 351.2 413.4 319.3 379.4 319.3C344.8 319.3 339.5 346.3 339.5 374.2L339.5 480L273.1 480L273.1 266.2L336.8 266.2L336.8 295.4L337.7 295.4C346.6 278.6 368.3 260.9 400.6 260.9C467.8 260.9 480.3 305.2 480.3 362.8L480.3 480z" fill="#fff"/>
</svg>`;

const SVG_X = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" aria-hidden="true">
	<path d="M453.2 112L523.8 112L369.6 288.2L551 528L409 528L297.7 382.6L170.5 528L99.8 528L264.7 339.5L90.8 112L236.4 112L336.9 244.9L453.2 112zM428.4 485.8L467.5 485.8L215.1 152L173.1 152L428.4 485.8z" fill="#fff"/>
</svg>`;

const SVG_YOUTUBE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" aria-hidden="true">
	<path d="M581.7 188.1C575.5 164.4 556.9 145.8 533.4 139.5C490.9 128 320.1 128 320.1 128C320.1 128 149.3 128 106.7 139.5C83.2 145.8 64.7 164.4 58.4 188.1C47 231 47 320.4 47 320.4C47 320.4 47 409.8 58.4 452.7C64.7 476.3 83.2 494.2 106.7 500.5C149.3 512 320.1 512 320.1 512C320.1 512 490.9 512 533.5 500.5C557 494.2 575.5 476.3 581.8 452.7C593.2 409.8 593.2 320.4 593.2 320.4C593.2 320.4 593.2 231 581.8 188.1zM264.2 401.6L264.2 239.2L406.9 320.4L264.2 401.6z" fill="#fff"/>
</svg>`;

const SVG_EXTERNAL_LINK = `<svg xmlns="http://www.w3.org/2000/svg"
	viewBox="0 0 24 24"
	fill="currentColor"
	focusable="false"
	aria-hidden="true">
	<path d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z"/>
	<path d="M5 5h6v2H7v10h10v-4h2v6H5V5z"/>
</svg>`;



// ---------------------------------------------------------------------------
/**
 * <lc-header>
 *
 * Renders a visually-hidden skip link followed by a <header> banner landmark.
 * The page-label attribute is reflected onto the inner <header>'s aria-label.
 *
 * @attr {string} page-label  - aria-label for the inner <header> element
 * @attr {string} logo-src    - URL for the header logo image
 *                              (default: /assets/ucam_language_centre_h_white.png)
 * @slot none
 */
// ---------------------------------------------------------------------------
class LcHeader extends HTMLElement {
	static get observedAttributes() {
		return ['page-label', 'logo-src'];
	}

	connectedCallback() {
		this.render();
	}

	attributeChangedCallback() {
		this.render();
	}

	render() {
		const label = escapeHTML(this.getAttribute('page-label') ?? 'Site header');
		const logoSrc = escapeHTML(this.getAttribute('logo-src') ?? './assets/ucam_language_centre_h_white.png');

		this.innerHTML = `
			<a href="#main-content" class="skip-link">Skip to main content</a>
			<header role="banner" aria-label="${label}" class="text-white bg-[var(--theme-band)]">
				<div class="max-w-6xl mx-auto px-4 h-20 flex items-center justify-between">
					<picture>
						<source media="(max-width: 639px)" srcset="${logoSrc}">
						<img src="${logoSrc}"
							alt="University of Cambridge Language Centre"
							class="h-10 md:h-12 w-auto">
					</picture>
				</div>
			</header>`;
	}
}


// ---------------------------------------------------------------------------
/**
 * <lc-footer>
 *
 * Renders the full shared footer: wordmark logo, LC square logo, social icons,
 * and copyright block. All content is static; the tagline and email can be
 * customised via attributes.
 *
 * @attr {string} tagline  - Footer tagline text
 *                           (default: "Connecting language learners")
 * @attr {string} email    - Contact email address
 *                           (default: enquiries@langcen.cam.ac.uk)
 * @slot none
 */
// ---------------------------------------------------------------------------
class LcFooter extends HTMLElement {
	connectedCallback() {
		this.render();
	}

	render() {
		const tagline = escapeHTML(this.getAttribute('tagline') ?? 'Connecting language learners');
		const email = escapeHTML(this.getAttribute('email') ?? 'enquiries@langcen.cam.ac.uk');

		this.innerHTML = `
			<footer role="contentinfo" class="site-footer mt-auto pb-16">
				<div class="footer-container">

					<div class="uclogo">
						<a href="https://www.langcen.cam.ac.uk/" target="_blank" rel="noopener noreferrer">
							<img class="footer-logo-desktop-white"
								alt="University of Cambridge Language Centre logo"
								src="./assets/ucam_language_centre_h_white.png">
							<img class="footer-logo-mobile-white"
								alt="University of Cambridge Language Centre logo"
								src="./assets/ucam_language_centre_v_white.png">
						</a>
					</div>

					<div class="square-logos">
						<a href="https://www.langcen.cam.ac.uk/culp/culp-index.html"
							target="_blank" rel="noopener noreferrer"
							title="Language Centre" aria-label="Language Centre">
							<div class="lclogo flex h-14 w-14 items-center justify-center rounded-md">
								${SVG_LC_LOGO}
							</div>
						</a>
					</div>

					<div class="social-logos">
						<ul class="cam-global-footer-links">
							<li>
								<a class="cam-social-media-icon" title="Facebook" aria-label="Facebook"
									href="https://facebook.com/uclangcen/">
									${SVG_FACEBOOK}
								</a>
							</li>
							<li>
								<a class="cam-social-media-icon" title="Instagram" aria-label="Instagram"
									href="https://instagram.com/cambridgeuniversity/">
									${SVG_INSTAGRAM}
								</a>
							</li>
							<li>
								<a class="cam-social-media-icon" title="LinkedIn" aria-label="LinkedIn"
									href="https://linkedin.com/company/94076110">
									${SVG_LINKEDIN}
								</a>
							</li>
							<li>
								<a class="cam-social-media-icon" title="X" aria-label="X"
									href="https://twitter.com/cambridge_uni">
									${SVG_X}
								</a>
							</li>
							<li>
								<a class="cam-social-media-icon" title="YouTube" aria-label="YouTube"
									href="https://youtube.com/cambridgeuniversity">
									${SVG_YOUTUBE}
								</a>
							</li>
						</ul>
					</div>

					<div class="copyright">
						<h2 class="footer-tagline">${tagline}</h2>
						<p class="copy">2026 &copy; University of Cambridge</p>
						<p class="developed">
							<a href="mailto:${email}">${email}</a>
						</p>
					</div>

				</div>
			</footer>`;
	}
}


// ---------------------------------------------------------------------------
/**
 * <lc-hero-poster>
 *
 * Renders the full-height hero panel: a decorative word cloud (aria-hidden)
 * and the artwork image. The poster gradient background is applied via the
 * poster-hero-bg utility class defined in main.css.
 *
 * @attr {string} artwork-src    - URL of the hero artwork image
 * @attr {string} artwork-alt    - Alt text for the artwork (default: "" — decorative)
 * @attr {string} artwork-class  - CSS classes for the img element
 *                                 (default: "hero-artwork-image h-[80%] w-auto opacity-95")
 * @slot none
 */
// ---------------------------------------------------------------------------
class LcHeroPoster extends HTMLElement {
	static get observedAttributes() {
		return ['artwork-src', 'artwork-alt', 'artwork-class'];
	}

	connectedCallback() {
		this.render();
	}

	attributeChangedCallback() {
		this.render();
	}

	render() {
		const src = escapeHTML(this.getAttribute('artwork-src') ?? '');
		const alt = escapeHTML(this.getAttribute('artwork-alt') ?? '');
		const imgClass = escapeHTML(this.getAttribute('artwork-class') ?? 'hero-artwork-image h-[80%] w-auto opacity-95');

		this.innerHTML = `
			<div class="poster-stage-conversation poster-hero-bg relative overflow-hidden rounded-[var(--radius-poster)] min-h-[24rem] md:min-h-[30rem] shadow-xl">

				<div class="absolute inset-0 z-0 flex flex-wrap content-start gap-x-6 gap-y-3 p-8 md:p-10 select-none text-[clamp(1rem,1.8vw,1.5rem)] font-semibold leading-none lowercase text-keyword"
					aria-hidden="true">
					<span>language learning</span><span>conversation</span><span>community</span><span>fluency</span><span>confidence</span><span>practice</span><span>cambridge</span><span>support</span><span>global</span><span>connections</span><span>culture</span><span>study</span><span>friendship</span><span>communication</span><span>opportunity</span><span>advice</span><span>exchange</span><span>languages</span>
				</div>

				<div class="hero-artwork absolute inset-0 z-10 flex items-end justify-start"
					aria-hidden="true">
					<img src="${src}" alt="${alt}" class="${imgClass}">
				</div>

			</div>`;
	}
}


// ---------------------------------------------------------------------------
/**
 * <lc-info-card>
 *
 * Renders the hero info card. Authored slot content (paragraphs, lists, links)
 * is placed between the component tags and re-injected into the card body.
 * Uses the Light DOM slot pattern: capture this.innerHTML before overwriting.
 *
 * @attr {string} heading     - Card h1 text
 * @attr {string} subheading  - Card h2 text
 * @slot default              - Body content (paragraphs, lists, links, etc.)
 */
// ---------------------------------------------------------------------------
class LcInfoCard extends HTMLElement {
	connectedCallback() {
		// Capture authored slot HTML before we overwrite it
		const bodyHTML = this.innerHTML;
		const heading = escapeHTML(this.getAttribute('heading') ?? '');
		const subheading = escapeHTML(this.getAttribute('subheading') ?? '');

		this.innerHTML = `
			<div class="self-center rounded-[var(--radius-poster)] p-6 md:p-8 lg:p-10 shadow-xl border bg-card border-soft shadow-soft">
				<h1 class="text-3xl md:text-4xl lg:text-5xl font-semibold leading-tight text-balance text-accent">
					${heading}
				</h1>
				<h2 class="mt-3 text-2xl font-semibold leading-tight text-balance text-main">
					${subheading}
				</h2>
				<div class="card-body">${bodyHTML}</div>
			</div>`;

		decorateExternalLinks(this);
	}
}


// ---------------------------------------------------------------------------
// Register all four components
// ---------------------------------------------------------------------------
customElements.define('lc-header', LcHeader);
customElements.define('lc-footer', LcFooter);
customElements.define('lc-hero-poster', LcHeroPoster);
customElements.define('lc-info-card', LcInfoCard);

function decorateExternalLinks(root) {
	root.querySelectorAll('a[href^="http://"], a[href^="https://"]').forEach((link) => {

		if (link.querySelector('.external-link-prefix')) {
			return;
		}

		const wrapper = document.createElement('span');
		wrapper.className = 'external-link-prefix';

		wrapper.innerHTML = `
			<span class="external-link-icon" aria-hidden="true">
				${SVG_EXTERNAL_LINK}
			</span>
		`;

		while (link.firstChild) {
			wrapper.appendChild(link.firstChild);
		}

		link.appendChild(wrapper);
	});
}
