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

				languageAdvisingStudyAbroad: resolve(
					__dirname,
					"language-advising-study-abroad.html"
				),

				oneToOneLanguageAdvisingAppointments: resolve(
					__dirname,
					"one-to-one-language-advising-appointments.html"
				),

				japaneseConversationHours: resolve(
					__dirname,
					"japanese-conversation-hours.html"
				),

				greekConversationHours: resolve(
					__dirname,
					"greek-conversation-hours.html"
				),

				portugueseConversationHours: resolve(
					__dirname,
					"portuguese-conversation-hours.html"
				)
			}
		}
	}
});