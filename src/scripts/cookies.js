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
			apiKey: '9c3bd2a68162ba67b19f07e540747675bd136e66',
			product: 'community',
			optionalCookies: [
				{
					name: 'analytics',
					label: 'Analytics',
					description: 'Analytical cookies help us to improve our website by collecting and reporting information on its usage.',
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
