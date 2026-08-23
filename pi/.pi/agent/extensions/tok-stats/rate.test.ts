import { describe, expect, test } from "bun:test";
import {
	MAX_PLAUSIBLE_RATE,
	MIN_RATE_CHUNKS,
	MIN_RATE_SPAN_MS,
	computeTokenRate,
	type RateWindow,
} from "./rate.ts";

// Healthy stream: first delta 500ms after start, end 3s, many chunks.
const healthy: RateWindow = { startTs: 0, endTs: 3000, firstDeltaTs: 500, chunkCount: 120 };

describe("computeTokenRate", () => {
	test("output tokens over decode span (first delta → end)", () => {
		// 200 tokens over 2.5s → 80 t/s
		expect(computeTokenRate(200, healthy)).toBe(80);
	});

	test("message start used as rate start when no delta timestamp", () => {
		// 200 tokens over 3s from start → ~66.67 t/s
		expect(computeTokenRate(200, { startTs: 0, endTs: 3000, chunkCount: 120 })).toBeCloseTo(66.67, 1);
	});

	test("no delta chunks at all → unmeasurable (non-streamed reply)", () => {
		expect(computeTokenRate(200, { startTs: 0, endTs: 3000, chunkCount: 0 })).toBeUndefined();
	});

	test("few-but-real chunks (4) still measure — short post-tool replies", () => {
		// 60 tokens over 0.9s → ~67 t/s
		expect(computeTokenRate(60, { startTs: 0, endTs: 1000, firstDeltaTs: 100, chunkCount: 4 })).toBeCloseTo(66.7, 1);
	});

	test("buffered burst: few chunks over tiny window → unmeasurable", () => {
		// Proxy buffered the whole reply, then flushed: 3117 tokens, all
		// chunks 100ms before end. Observed span says ~31k t/s — impossible.
		expect(
			computeTokenRate(3117, { startTs: 0, endTs: 1800, firstDeltaTs: 1700, chunkCount: 3 }),
		).toBeUndefined();
	});

	test("rate above physical ceiling → unmeasurable", () => {
		// The observed bug: 1200 tokens in 0.7s ≈ 1714 t/s while chunks were
		// plentiful — only possible if delivery was bursty, so reject.
		expect(computeTokenRate(1200, { startTs: 0, endTs: 700, firstDeltaTs: 0, chunkCount: 50 })).toBeUndefined();
	});

	test("span below floor → unmeasurable even with many chunks", () => {
		expect(computeTokenRate(50, { startTs: 0, endTs: MIN_RATE_SPAN_MS - 1, firstDeltaTs: 0, chunkCount: 50 })).toBeUndefined();
	});

	test("boundary: exactly MIN_RATE_CHUNKS and MIN_RATE_SPAN_MS still measure", () => {
		// 400 tokens over 1s = 400 t/s, at ceiling, not above it.
		expect(
			computeTokenRate(MAX_PLAUSIBLE_RATE, {
				startTs: 0,
				endTs: 1000,
				firstDeltaTs: 0,
				chunkCount: MIN_RATE_CHUNKS,
			}),
		).toBe(MAX_PLAUSIBLE_RATE);
	});

	test("zero output → undefined", () => {
		expect(computeTokenRate(0, healthy)).toBeUndefined();
	});

	test("negative output → undefined", () => {
		expect(computeTokenRate(-1, healthy)).toBeUndefined();
	});
});
