/**
 * Shared CookieControl configuration for LC postcard pages.
 *
 * Google Analytics is loaded only after the user accepts the optional
 * analytics cookie category.
 */

(function () {
	var GA_MEASUREMENT_ID = 'G-1PVV9JSR1M';
	var gaLoaded = false;

	function loadGoogleAnalytics() {
		if (gaLoaded || window.gtag) {
			gaLoaded = true;
			return;
		}

		var script = document.createElement('script');
		script.async = true;
		script.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_MEASUREMENT_ID;
		document.head.appendChild(script);

		window.dataLayer = window.dataLayer || [];
		window.gtag = function () {
			window.dataLayer.push(arguments);
		};

		window.gtag('js', new Date());
		window.gtag('config', GA_MEASUREMENT_ID);

		gaLoaded = true;
	}

	function revokeGoogleAnalytics() {
		if (window.gtag) {
			window.gtag('consent', 'update', {
				analytics_storage: 'denied'
			});
		}
	}

	function loadCookieControl() {
		if (!window.CookieControl) {
			return;
		}

		var config = {
			apiKey: '4850434eebae9bebd89d752afb7e7b0ca0f977e0',
			product: 'COMMUNITY',
			optionalCookies: [
				{
					name: 'analytics',
					label: 'Analytical Cookies',
					description: 'Analytical cookies help us to improve our website by collecting and reporting information on its usage.',

					// Named so Cookie Control can clear them on revoke, and so the
					// banner's cookie list matches what GA4 actually sets.
					cookies: [
						'_ga',
						'_ga_' + GA_MEASUREMENT_ID.replace('G-', '')
					],
					onAccept: function () {
						loadGoogleAnalytics();
					},
					onRevoke: function () {
						revokeGoogleAnalytics();
					}
				},
				{
					name: 'marketing',
					label: 'Marketing Cookies',
					description: 'We use marketing cookies to help us improve the relevancy of advertising campaigns you receive.',

					// Declared for parity with the main site's banner. These pages run
					// no advertising, so there is nothing to load or clear — wire the
					// handlers up if that ever changes.
					cookies: [],
					onAccept: function () {},
					onRevoke: function () {}
				}
			],
			position: 'LEFT',
			theme: 'LIGHT'
		};

		window.CookieControl.load(config);
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', loadCookieControl);
	} else {
		loadCookieControl();
	}
}());
