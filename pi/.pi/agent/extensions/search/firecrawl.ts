export interface SearchParams {
	query: string;
	limit?: number;
}

export interface SearchResult {
	text: string;
	isError: boolean;
	details: {
		query: string;
		count: number;
		creditsUsed?: number;
	};
}

interface SearchOptions {
	fetch?: typeof fetch;
	signal?: AbortSignal;
}

interface WebHit {
	url?: string;
	title?: string;
	description?: string;
	position?: number;
}

interface FirecrawlSearchPayload {
	success?: boolean;
	error?: string;
	data?: {
		web?: WebHit[];
	};
	creditsUsed?: number;
}

function isAbortError(error: unknown): boolean {
	return error instanceof Error && error.name === "AbortError";
}

export async function searchFirecrawl(
	params: SearchParams,
	options: SearchOptions = {},
): Promise<SearchResult> {
	const fetchFn = options.fetch ?? globalThis.fetch;
	let response: Response;
	try {
		response = await fetchFn("https://api.firecrawl.dev/v2/search", {
			method: "POST",
			headers: { "content-type": "application/json" },
			body: JSON.stringify({ query: params.query, limit: params.limit ?? 5 }),
			signal: options.signal,
		});
	} catch (error) {
		if (isAbortError(error)) throw error;
		const message = error instanceof Error ? error.message : String(error);
		return {
			text: `Firecrawl search failed: ${message}`,
			isError: true,
			details: { query: params.query, count: 0 },
		};
	}
	let payload: FirecrawlSearchPayload;
	try {
		payload = (await response.json()) as FirecrawlSearchPayload;
	} catch {
		return {
			text: `Firecrawl search failed: HTTP ${response.status}`,
			isError: true,
			details: { query: params.query, count: 0 },
		};
	}
	if (payload.success === false) {
		return {
			text: `Firecrawl search failed: ${payload.error ?? "unknown error"}`,
			isError: true,
			details: { query: params.query, count: 0 },
		};
	}
	const hits = payload.data?.web ?? [];
	if (hits.length === 0) {
		return {
			text: "No results.",
			isError: false,
			details: { query: params.query, count: 0, creditsUsed: payload.creditsUsed },
		};
	}
	const lines: string[] = [];
	for (const [index, hit] of hits.entries()) {
		const rank = hit.position ?? index + 1;
		const heading = hit.title ?? hit.url;
		if (!heading) continue;
		if (lines.length > 0) lines.push("");
		lines.push(`${rank}. ${heading}`);
		if (hit.url && hit.url !== heading) lines.push(`   ${hit.url}`);
		if (hit.description) lines.push(`   ${hit.description}`);
	}
	return {
		text: lines.join("\n"),
		isError: false,
		details: {
			query: params.query,
			count: hits.length,
			creditsUsed: payload.creditsUsed,
		},
	};
}
