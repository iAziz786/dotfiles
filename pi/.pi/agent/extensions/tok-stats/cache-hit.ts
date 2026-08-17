/**
 * Last-turn cache miss, same rules as pi `/session` (`cache-stats.js`).
 *
 * A miss is previous-prompt tokens that should have been cache reads but were
 * re-billed. Hits (and first turn / post-compaction / no-cache providers) are
 * not misses. Re-bills at or below 1024 tokens are noise.
 *
 * Session entries store role/usage on `entry.message`, not the entry itself.
 */

export type CacheUsage = {
	input: number;
	cacheRead: number;
	cacheWrite: number;
};

export type CacheScanEntry =
	| { type: "compaction" }
	| { type: "branch_summary" }
	| { type: "message"; message: { role: string; usage?: CacheUsage } }
	| { type: string; message?: { role?: string; usage?: CacheUsage } };

type PreviousRequest = {
	promptTokens: number;
	reportedCache: boolean;
};

/** Per-turn misses at or below this are cache breakpoint granularity noise. */
const NOISE_FLOOR_TOKENS = 1024;

function promptTokens(usage: CacheUsage): number {
	return usage.input + usage.cacheRead + usage.cacheWrite;
}

function detectMiss(prev: PreviousRequest | undefined, usage: CacheUsage): boolean {
	const tokens = promptTokens(usage);
	// A zero-cache turn only counts when cache activity was reported before:
	// on cache-read-only providers that is a total miss, while on providers
	// that never report caching it means nothing.
	if (!prev || tokens <= 0 || (usage.cacheRead + usage.cacheWrite === 0 && !prev.reportedCache)) {
		return false;
	}
	return Math.min(prev.promptTokens, tokens) - usage.cacheRead > NOISE_FLOOR_TOKENS;
}

function asPreviousRequest(usage: CacheUsage, reportedCache: boolean): PreviousRequest | undefined {
	const tokens = promptTokens(usage);
	if (tokens <= 0) return undefined;
	return {
		promptTokens: tokens,
		reportedCache: reportedCache || usage.cacheRead + usage.cacheWrite > 0,
	};
}

export function lastAssistantWasCacheMiss(entries: readonly CacheScanEntry[]): boolean {
	let prev: PreviousRequest | undefined;
	let lastWasMiss = false;
	for (const entry of entries) {
		if (entry.type === "compaction" || entry.type === "branch_summary") {
			// Context legitimately changed; next turn is new content, not re-billed.
			prev = undefined;
			continue;
		}
		if (entry.type !== "message" || entry.message?.role !== "assistant" || !entry.message.usage) continue;
		lastWasMiss = detectMiss(prev, entry.message.usage);
		prev = asPreviousRequest(entry.message.usage, prev?.reportedCache ?? false) ?? prev;
	}
	return lastWasMiss;
}

export type CacheHitColor = "success" | "error";

export function cacheHitThemeColor(isMiss: boolean): CacheHitColor {
	return isMiss ? "error" : "success";
}
