import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
	base: "./",
	build: {
		rollupOptions: {
			input: {
				index: resolve(__dirname, "index.html"),

				englishConversationHours: resolve(
					__dirname,
					"english-conversation-hours.html"
				),

				intermediateConversationHours: resolve(
					__dirname,
					"intermediate-conversation-hours.html"
				),

				advancedConversationHours: resolve(
					__dirname,
					"advanced-conversation-hours.html"
				),

				conversationExchange: resolve(
					__dirname,
					"conversation-exchange.html"
				),

				friendsWithoutFrontiers: resolve(
					__dirname,
					"friends-without-frontiers.html"
				),

				portugueseConversationHours: resolve(
					__dirname,
					"portuguese-conversation-hours.html"
				),

				languageAdvising: resolve(
					__dirname,
					"language-advising.html"
				),

				studyAbroad: resolve(
					__dirname,
					"study-abroad.html"
				),

				visitOurStudyCentre: resolve(
					__dirname,
					"visit-our-study-centre.html"
				)
			}
		}
	}
});
