/**
 * Shared CookieControl configuration for LC postcard pages.
 */

(function () {
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
					cookies: [],
					onAccept: function () { },
					onRevoke: function () { }
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
