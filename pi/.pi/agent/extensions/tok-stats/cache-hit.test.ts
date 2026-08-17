import { describe, expect, test } from "bun:test";
import { cacheHitThemeColor, lastAssistantWasCacheMiss, type CacheScanEntry } from "./cache-hit.ts";

function usage(input: number, cacheRead: number, cacheWrite = 0) {
	return { input, cacheRead, cacheWrite };
}

function assistant(input: number, cacheRead: number, cacheWrite = 0): CacheScanEntry {
	return { type: "message", message: { role: "assistant", usage: usage(input, cacheRead, cacheWrite) } };
}

describe("lastAssistantWasCacheMiss", () => {
	test("first turn is not a miss", () => {
		expect(lastAssistantWasCacheMiss([assistant(5000, 0, 5000)])).toBe(false);
	});

	test("full cache read of previous prompt is a hit", () => {
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				assistant(200, 10_000),
			]),
		).toBe(false);
	});

	test("re-billed previous tokens above 1024 is a miss", () => {
		// prev prompt 10_000; this turn only reads 5_000 from cache
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				assistant(5_000, 5_000),
			]),
		).toBe(true);
	});

	test("re-billed tokens at or below 1024 noise floor is not a miss", () => {
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				assistant(1024, 8_976),
			]),
		).toBe(false);
	});

	test("zero-cache turn after cache was reported is a miss", () => {
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				assistant(10_000, 0, 0),
			]),
		).toBe(true);
	});

	test("zero-cache turn when provider never reported cache is not a miss", () => {
		expect(
			lastAssistantWasCacheMiss([
				assistant(10_000, 0, 0),
				assistant(12_000, 0, 0),
			]),
		).toBe(false);
	});

	test("compaction resets previous prompt so next turn is not a miss", () => {
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				{ type: "compaction" },
				assistant(10_000, 0, 0),
			]),
		).toBe(false);
	});

	test("branch_summary also resets previous prompt", () => {
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				{ type: "branch_summary" },
				assistant(10_000, 0, 0),
			]),
		).toBe(false);
	});

	test("uses last assistant turn only", () => {
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				assistant(5_000, 5_000), // miss
				assistant(200, 10_000), // hit
			]),
		).toBe(false);
		expect(
			lastAssistantWasCacheMiss([
				assistant(0, 0, 10_000),
				assistant(200, 10_000), // hit
				assistant(5_000, 5_000), // miss
			]),
		).toBe(true);
	});

	test("reads role/usage from entry.message (session shape)", () => {
		// Flat entry.role would miss this and always return false.
		expect(
			lastAssistantWasCacheMiss([
				{ type: "message", message: { role: "assistant", usage: usage(0, 0, 10_000) } },
				{ type: "message", message: { role: "assistant", usage: usage(5_000, 5_000) } },
			]),
		).toBe(true);
	});
});

describe("cacheHitThemeColor", () => {
	test("hit is success/green", () => {
		expect(cacheHitThemeColor(false)).toBe("success");
	});

	test("miss is error/red", () => {
		expect(cacheHitThemeColor(true)).toBe("error");
	});
});
