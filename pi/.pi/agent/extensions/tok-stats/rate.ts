/**
 * Decode throughput: output tokens / seconds from rate start to end.
 * Rate start = first stream delta when present, else message start (no-delta fallback).
 * Only rejects non-positive output or non-positive span (same-tick / inverted clocks).
 */
export function computeTokenRate(
	outputTokens: number,
	startTs: number,
	endTs: number,
	firstDeltaTs?: number,
): number | undefined {
	if (outputTokens <= 0) return undefined;
	const rateStartTs = firstDeltaTs ?? startTs;
	const spanMs = endTs - rateStartTs;
	if (spanMs <= 0) return undefined;
	return outputTokens / (spanMs / 1000);
}
