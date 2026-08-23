/**
 * Decode throughput: output tokens / seconds from first stream delta to end.
 *
 * The span is only trustworthy when delivery was genuinely incremental. A
 * proxy that buffers the whole reply and flushes it in one burst compresses
 * the observed span to near zero, producing impossible rates (thousands of
 * t/s). Such measurements are rejected and reported as unmeasurable.
 */

/** Fewer stream events than this over the window means burst delivery. */
export const MIN_RATE_CHUNKS = 4;

/** Spans shorter than this cannot resolve a decode rate. */
export const MIN_RATE_SPAN_MS = 300;

/** Public decode ceilings run a few hundred t/s; anything above is suspect. */
export const MAX_PLAUSIBLE_RATE = 400;

export interface RateWindow {
	/** message_start timestamp (post-HTTP-headers, pre-first-chunk). */
	startTs: number;
	/** message_end timestamp. */
	endTs: number;
	/** First delta timestamp; falls back to startTs when absent. */
	firstDeltaTs?: number;
	/** Number of streamed delta events observed (text/thinking/toolcall). */
	chunkCount: number;
}

export function computeTokenRate(outputTokens: number, window: RateWindow): number | undefined {
	if (outputTokens <= 0) return undefined;
	const rateStartTs = window.firstDeltaTs ?? window.startTs;
	const spanMs = window.endTs - rateStartTs;
	// Burst-flushed or too-short-to-measure delivery.
	if (window.chunkCount < MIN_RATE_CHUNKS || spanMs < MIN_RATE_SPAN_MS) return undefined;
	const rate = outputTokens / (spanMs / 1000);
	// Plausible only below the physical decode ceiling. The ceiling is the
	// primary burst catch; the chunk floor only guards sub-ceiling flushes.
	if (!Number.isFinite(rate) || rate > MAX_PLAUSIBLE_RATE) return undefined;
	return rate;
}
