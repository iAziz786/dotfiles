import { describe, expect, test } from "bun:test";
import { searchFirecrawl } from "./firecrawl.ts";

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "content-type": "application/json" },
	});
}

describe("searchFirecrawl", () => {
	test("formats web hits from a successful Firecrawl payload", async () => {
		const fetchFn = async () =>
			jsonResponse({
				success: true,
				data: {
					web: [
						{
							url: "https://pi.dev/",
							title: "Pi Coding Agent",
							description: "Customize Pi with extensions.",
							position: 1,
						},
						{
							url: "https://github.com/badlogic/pi-mono",
							title: "pi-mono",
							description: "The pi monorepo.",
							position: 2,
						},
					],
				},
				creditsUsed: 2,
			});

		const result = await searchFirecrawl({ query: "pi coding agent" }, { fetch: fetchFn });

		expect(result.text).toBe(
			[
				"1. Pi Coding Agent",
				"   https://pi.dev/",
				"   Customize Pi with extensions.",
				"",
				"2. pi-mono",
				"   https://github.com/badlogic/pi-mono",
				"   The pi monorepo.",
			].join("\n"),
		);
		expect(result.isError).toBe(false);
		expect(result.details).toEqual({ query: "pi coding agent", count: 2, creditsUsed: 2 });
	});

	test("surfaces Firecrawl error payload", async () => {
		const fetchFn = async () =>
			jsonResponse(
				{
					success: false,
					error: "Invalid request body",
				},
				400,
			);

		const result = await searchFirecrawl({ query: "pi" }, { fetch: fetchFn });

		expect(result.isError).toBe(true);
		expect(result.text).toBe("Firecrawl search failed: Invalid request body");
		expect(result.details).toEqual({ query: "pi", count: 0 });
	});

	test("POSTs keyless JSON to /v2/search", async () => {
		let request: Request | undefined;
		const fetchFn = async (input: RequestInfo | URL, init?: RequestInit) => {
			request = new Request(input, init);
			return jsonResponse({ success: true, data: { web: [] } });
		};

		const result = await searchFirecrawl({ query: "pi coding agent", limit: 3 }, { fetch: fetchFn });

		expect(request).toBeDefined();
		expect(request!.method).toBe("POST");
		expect(request!.url).toBe("https://api.firecrawl.dev/v2/search");
		expect(request!.headers.get("authorization")).toBeNull();
		expect(request!.headers.get("content-type")).toBe("application/json");
		expect(await request!.json()).toEqual({ query: "pi coding agent", limit: 3 });
		expect(result.text).toBe("No results.");
		expect(result.details.count).toBe(0);
	});

	test("forwards abort signal to fetch", async () => {
		const signal = new AbortController().signal;
		let received: AbortSignal | undefined;
		const fetchFn = async (_input: RequestInfo | URL, init?: RequestInit) => {
			received = init?.signal ?? undefined;
			return jsonResponse({ success: true, data: { web: [] } });
		};

		await searchFirecrawl({ query: "pi" }, { fetch: fetchFn, signal });

		expect(received).toBe(signal);
	});

	test("surfaces HTTP failure when body is not JSON", async () => {
		const fetchFn = async () => new Response("<html>nope</html>", { status: 502 });

		const result = await searchFirecrawl({ query: "pi" }, { fetch: fetchFn });

		expect(result.isError).toBe(true);
		expect(result.text).toBe("Firecrawl search failed: HTTP 502");
	});

	test("rethrows abort errors", async () => {
		const fetchFn = async () => {
			throw new DOMException("The operation was aborted.", "AbortError");
		};

		await expect(searchFirecrawl({ query: "pi" }, { fetch: fetchFn })).rejects.toMatchObject({
			name: "AbortError",
		});
	});

	test("surfaces network failures", async () => {
		const fetchFn = async () => {
			throw new TypeError("fetch failed");
		};

		const result = await searchFirecrawl({ query: "pi" }, { fetch: fetchFn });

		expect(result.isError).toBe(true);
		expect(result.text).toBe("Firecrawl search failed: fetch failed");
	});

	test("skips missing title, url, or description", async () => {
		const fetchFn = async () =>
			jsonResponse({
				success: true,
				data: {
					web: [{ url: "https://pi.dev/", position: 1 }],
				},
			});

		const result = await searchFirecrawl({ query: "pi" }, { fetch: fetchFn });

		expect(result.text).toBe("1. https://pi.dev/");
	});
});
