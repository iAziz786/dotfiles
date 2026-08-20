/**
 * Firecrawl Keyless search tool.
 *
 * POST https://api.firecrawl.dev/v2/search — no Authorization header.
 * 1,000 free credits / month. Sign up only when you need more.
 * https://www.firecrawl.dev/blog/firecrawl-keyless-launch
 */

import { Type } from "typebox";
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { searchFirecrawl } from "./firecrawl.ts";

const searchTool = defineTool({
	name: "search",
	label: "Search",
	description:
		"Search the live web via Firecrawl Keyless. Returns titles, URLs, and snippets. No API key required.",
	promptSnippet: "Search the live web and return titles, URLs, and snippets",
	promptGuidelines: [
		"Use search when the user asks to look something up on the web, research a topic, or needs current information.",
	],
	parameters: Type.Object({
		query: Type.String({ description: "Search query" }),
		limit: Type.Optional(Type.Number({ description: "Max results (default 5, max 100)" })),
	}),
	async execute(_toolCallId, params, signal) {
		const result = await searchFirecrawl(params, { signal });
		if (result.isError) throw new Error(result.text);
		return {
			content: [{ type: "text", text: result.text }],
			details: result.details,
		};
	},
});

export default function (pi: ExtensionAPI) {
	// NOTE: search tool disabled for now. Re-enable by uncommenting.
	// pi.registerTool(searchTool);
}
