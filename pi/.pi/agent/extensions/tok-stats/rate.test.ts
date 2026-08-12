import { describe, expect, test } from "bun:test";
import { computeTokenRate } from "./rate.ts";

describe("computeTokenRate", () => {
	test("output tokens over decode span", () => {
		// 200 tokens in 2s → 100 t/s
		expect(computeTokenRate(200, 1000, 3000)).toBe(100);
	});

	test("uses first delta as rate start when present", () => {
		// start=500, firstDelta=1000, end=3000 → span 2s → 100 t/s (not 2.5s from start)
		expect(computeTokenRate(200, 500, 3000, 1000)).toBe(100);
	});

	test("falls back to message start when no deltas", () => {
		// no firstDelta → wall span start→end
		expect(computeTokenRate(200, 1000, 3000, undefined)).toBe(100);
	});

	test("includes time after last delta (end - first, not last - first)", () => {
		// Old bug: lastDelta=1500, first=1000 → span 0.5s → 400 t/s inflated.
		// Correct: end=3000, first=1000 → span 2s → 100 t/s.
		expect(computeTokenRate(200, 0, 3000, 1000)).toBe(100);
	});

	test("single-chunk stream still measurable via end timestamp", () => {
		// One delta at t=1000, message_end at t=2500, 150 tokens.
		expect(computeTokenRate(150, 0, 2500, 1000)).toBe(100);
	});

	test("short spans still yield a rate when span > 0", () => {
		// 50 tokens in 50ms → 1000 t/s (old min-span floor would drop this)
		expect(computeTokenRate(50, 1000, 1050, 1000)).toBe(1000);
	});

	test("undefined when span is zero", () => {
		expect(computeTokenRate(50, 1000, 1000, 1000)).toBeUndefined();
	});

	test("undefined when span is negative", () => {
		expect(computeTokenRate(50, 1000, 900, 1000)).toBeUndefined();
	});

	test("undefined when no output tokens", () => {
		expect(computeTokenRate(0, 1000, 3000)).toBeUndefined();
	});

	test("undefined when negative output", () => {
		expect(computeTokenRate(-1, 1000, 3000)).toBeUndefined();
	});
});
