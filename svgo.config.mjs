/**
 * Optimises the designer's illustrations for the web.
 *
 * The supplied files are almost entirely path data, so the ordinary SVGO
 * defaults only save about 8%. Reducing coordinate precision to one decimal
 * place halves them instead: 982 KB of brotli-compressed SVG becomes 510 KB.
 *
 * One decimal place is safe here because the viewBoxes are roughly 900 units
 * wide, so 0.1 of a unit is about 0.01% of the drawing's width. Rendering
 * before and after at display size differs only in edge antialiasing, and the
 * two are indistinguishable even magnified 4x on the most detailed drawing.
 *
 * Run after the designer supplies new artwork:
 *
 *     bun run assets:svg
 */
export default {
	multipass: true,
	floatPrecision: 1,
	plugins: [
		// cleanupIds is off: the drawings use referenced clip paths and
		// gradients, and renaming those has broken them before.
		{ name: 'preset-default', params: { overrides: { cleanupIds: false } } },

		// The markup sets the size, so intrinsic width/height only fight it.
		'removeDimensions',

		{ name: 'convertPathData', params: { floatPrecision: 1, transformPrecision: 2 } },
	],
};
