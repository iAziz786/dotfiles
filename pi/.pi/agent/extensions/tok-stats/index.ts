/**
 * Custom footer with token throughput.
 *
 * Reimplements the built-in footer (pwd line + stats line + extension statuses)
 * and inserts an exact t/s segment into the stats line, right after the R cache
 * segment: `↑88k ↓43k R5.2M 78 t/s CH99.9% $0.069 7.3%/1.0M (auto)`.
 *
 * Shows exact decode rate after each response (output tokens / time from first
 * stream delta to message_end; falls back to message_start when no deltas).
 * Any positive span counts — no min-span floor. `0 t/s` when unmeasurable.
 * No live estimate during streaming.
 *
 * Approximations vs built-in footer (fields not exposed to extensions):
 *  - "(auto)" auto-compact indicator rendered statically
 *  - kimi-coding "(sub)" marker via provider-name check instead of runtime probe
 */

import { isAbsolute, relative, resolve, sep } from "node:path";
import { truncateToWidth, visibleWidth, type TUI } from "@earendil-works/pi-tui";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import type { AssistantMessage, Usage } from "@earendil-works/pi-ai";
import { cacheHitThemeColor, lastAssistantWasCacheMiss } from "./cache-hit.ts";
import { computeTokenRate } from "./rate.ts";

interface UsageTotals {
	input: number;
	output: number;
	cacheRead: number;
	cacheWrite: number;
	cost: number;
}

interface Stream {
	startTs: number;
	firstDeltaTs: number | undefined;
}

function nowMs(): number {
	return performance.now();
}

function createUsageTotals(): UsageTotals {
	return { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, cost: 0 };
}

function addUsageToTotals(totals: UsageTotals, usage: Usage): void {
	totals.input += usage.input;
	totals.output += usage.output;
	totals.cacheRead += usage.cacheRead;
	totals.cacheWrite += usage.cacheWrite;
	totals.cost += usage.cost.total;
}

function formatTokens(count: number): string {
	if (count < 1000) return count.toString();
	if (count < 10000) return `${(count / 1000).toFixed(1)}k`;
	if (count < 1000000) return `${Math.round(count / 1000)}k`;
	if (count < 10000000) return `${(count / 1000000).toFixed(1)}M`;
	return `${Math.round(count / 1000000)}M`;
}

function formatCwdForFooter(cwd: string, home: string | undefined): string {
	if (!home) return cwd;
	const resolvedCwd = resolve(cwd);
	const resolvedHome = resolve(home);
	const relativeToHome = relative(resolvedHome, resolvedCwd);
	const isInsideHome =
		relativeToHome === "" ||
		(relativeToHome !== ".." && !relativeToHome.startsWith(`..${sep}`) && !isAbsolute(relativeToHome));
	if (!isInsideHome) return cwd;
	return relativeToHome === "" ? "~" : `~${sep}${relativeToHome}`;
}

function sanitizeStatusText(text: string): string {
	return text
		.replace(/[\r\n\t]/g, " ")
		.replace(/ +/g, " ")
		.trim();
}

export default function (pi: ExtensionAPI) {
	let current: Stream | undefined;
	let lastRate: number | undefined; // exact t/s from last completed message
	let latestCtx: ExtensionContext | undefined;
	let tui: TUI | undefined;
	let footerSet = false;

	function ensureFooter(ctx: ExtensionContext): void {
		if (footerSet || ctx.mode !== "tui") return;
		footerSet = true;
		latestCtx = ctx;
		ctx.ui.setFooter((tuiArg, theme, footerData) => {
			tui = tuiArg;
			const dispose = footerData.onBranchChange(() => tuiArg.requestRender());
			return {
				dispose,
				invalidate() {},
				render(width: number): string[] {
					const ctx2 = latestCtx;
					if (!ctx2) return [];
					const entries = ctx2.sessionManager.getEntries();

					// Cumulative usage from ALL session entries (matches built-in footer).
					const usageTotals = createUsageTotals();
					let latestCacheHitRate: number | undefined;
					for (const entry of entries) {
						if (entry.type === "message" && entry.message.role === "assistant") {
							const m = entry.message as AssistantMessage;
							addUsageToTotals(usageTotals, m.usage);
							const latestPromptTokens = m.usage.input + m.usage.cacheRead + m.usage.cacheWrite;
							latestCacheHitRate =
								latestPromptTokens > 0 ? (m.usage.cacheRead / latestPromptTokens) * 100 : undefined;
						} else if (entry.type === "message" && entry.message.role === "toolResult" && entry.message.usage) {
							addUsageToTotals(usageTotals, entry.message.usage);
						} else if ((entry.type === "branch_summary" || entry.type === "compaction") && entry.usage) {
							addUsageToTotals(usageTotals, entry.usage);
						}
					}

					// Context usage (handles compaction).
					const contextUsage = ctx2.getContextUsage();
					const contextWindow = contextUsage?.contextWindow ?? ctx2.model?.contextWindow ?? 0;
					const contextPercentValue = contextUsage?.percent ?? 0;
					const contextPercent = contextUsage?.percent !== null ? contextPercentValue.toFixed(1) : "?";

					// pwd line: cwd + git branch + session name.
					let pwd = formatCwdForFooter(ctx2.sessionManager.getCwd(), process.env.HOME || process.env.USERPROFILE);
					const branch = footerData.getGitBranch();
					if (branch) pwd = `${pwd} (${branch})`;
					const sessionName = ctx2.sessionManager.getSessionName();
					if (sessionName) pwd = `${pwd} • ${sessionName}`;

					// Stats line. Dim each segment individually; t/s and CH are colored separately,
					// because an embedded color reset (\x1b[39m) would wipe the dim for everything after it.
					const dim = (s: string): string => theme.fg("dim", s);
					const statsParts: string[] = [];
					if (usageTotals.input) statsParts.push(dim(`↑${formatTokens(usageTotals.input)}`));
					if (usageTotals.output) statsParts.push(dim(`↓${formatTokens(usageTotals.output)}`));
					if (usageTotals.cacheRead) statsParts.push(dim(`R${formatTokens(usageTotals.cacheRead)}`));

					// t/s segment (right after R). Exact rate from last completed message, else 0.
					statsParts.push(theme.fg("accent", `${lastRate !== undefined ? Math.round(lastRate) : 0} t/s`));

					if (usageTotals.cacheWrite) statsParts.push(dim(`W${formatTokens(usageTotals.cacheWrite)}`));
					if ((usageTotals.cacheRead > 0 || usageTotals.cacheWrite > 0) && latestCacheHitRate !== undefined) {
						statsParts.push(
							theme.fg(
								cacheHitThemeColor(lastAssistantWasCacheMiss(entries)),
								`CH${latestCacheHitRate.toFixed(1)}%`,
							),
						);
					}
					const usingSubscription = ctx2.model?.provider === "kimi-coding";
					if (usageTotals.cost || usingSubscription) {
						statsParts.push(dim(`$${usageTotals.cost.toFixed(3)}${usingSubscription ? " (sub)" : ""}`));
					}
					const autoIndicator = " (auto)";
					const contextPercentDisplay =
						contextPercent === "?"
							? `?/${formatTokens(contextWindow)}${autoIndicator}`
							: `${contextPercent}%/${formatTokens(contextWindow)}${autoIndicator}`;
					let contextPercentStr: string;
					if (contextPercentValue > 90) contextPercentStr = theme.fg("error", contextPercentDisplay);
					else if (contextPercentValue > 70) contextPercentStr = theme.fg("warning", contextPercentDisplay);
					else contextPercentStr = dim(contextPercentDisplay);
					statsParts.push(contextPercentStr);

					let statsLeft = statsParts.join(" ");
					const modelName = ctx2.model?.id || "no-model";
					let statsLeftWidth = visibleWidth(statsLeft);
					if (statsLeftWidth > width) {
						statsLeft = truncateToWidth(statsLeft, width, "...");
						statsLeftWidth = visibleWidth(statsLeft);
					}
					const minPadding = 2;
					let rightSideWithoutProvider = modelName;
					if (ctx2.model?.reasoning) {
						const thinkingLevel = ctx2.thinkingLevel ?? "off";
						rightSideWithoutProvider =
							thinkingLevel === "off" ? `${modelName} • thinking off` : `${modelName} • ${thinkingLevel}`;
					}
					let rightSide = rightSideWithoutProvider;
					if (footerData.getAvailableProviderCount() > 1 && ctx2.model) {
						rightSide = `(${ctx2.model.provider}) ${rightSideWithoutProvider}`;
						if (statsLeftWidth + minPadding + visibleWidth(rightSide) > width) {
							rightSide = rightSideWithoutProvider;
						}
					}
					const rightSideWidth = visibleWidth(rightSide);
					const totalNeeded = statsLeftWidth + minPadding + rightSideWidth;
					let statsLine: string;
					if (totalNeeded <= width) {
						const padding = " ".repeat(width - statsLeftWidth - rightSideWidth);
						statsLine = statsLeft + padding + rightSide;
					} else {
						const availableForRight = width - statsLeftWidth - minPadding;
						if (availableForRight > 0) {
							const truncatedRight = truncateToWidth(rightSide, availableForRight, "");
							const truncatedRightWidth = visibleWidth(truncatedRight);
							const padding = " ".repeat(Math.max(0, width - statsLeftWidth - truncatedRightWidth));
							statsLine = statsLeft + padding + truncatedRight;
						} else {
							statsLine = statsLeft;
						}
					}

					// remainder is padding + rightSide; statsLeft is already individually styled.
					const remainder = statsLine.slice(statsLeft.length);
					const dimRemainder = theme.fg("dim", remainder);
					const pwdLine = truncateToWidth(theme.fg("dim", pwd), width, theme.fg("dim", "..."));

					const lines = [pwdLine, statsLeft + dimRemainder];
					// Keep extension statuses line (other extensions' setStatus output).
					const extensionStatuses = footerData.getExtensionStatuses();
					if (extensionStatuses.size > 0) {
						const sortedStatuses = Array.from(extensionStatuses.entries())
							.sort(([a], [b]) => a.localeCompare(b))
							.map(([, text]) => sanitizeStatusText(text));
						lines.push(truncateToWidth(sortedStatuses.join(" "), width, theme.fg("dim", "...")));
					}
					return lines;
				},
			};
		});
	}

	let renderTimer: ReturnType<typeof setTimeout> | undefined;

	function requestRender(): void {
		tui?.requestRender();
	}

	// Defer past session persistence: message_end fires before the new message
	// lands in session entries (see pi interactive-mode), so rendering on the
	// same frame would show fresh t/s with stale ↑↓ counts. A short delay makes
	// both land on one frame, matching built-in footer cadence.
	function clearRenderTimer(): void {
		if (renderTimer !== undefined) {
			clearTimeout(renderTimer);
			renderTimer = undefined;
		}
	}

	function scheduleRender(): void {
		clearRenderTimer();
		renderTimer = setTimeout(() => {
			renderTimer = undefined;
			requestRender();
		}, 100);
	}

	pi.on("session_start", (event, ctx) => {
		latestCtx = ctx;
		lastRate = undefined;
		current = undefined;
		ensureFooter(ctx);
	});

	pi.on("session_shutdown", () => {
		clearRenderTimer();
		current = undefined;
		lastRate = undefined;
		tui = undefined;
		latestCtx = undefined;
	});

	pi.on("message_start", (event, ctx) => {
		latestCtx = ctx;
		ensureFooter(ctx);
		if (event.message.role !== "assistant") return;
		current = { startTs: nowMs(), firstDeltaTs: undefined };
	});

	pi.on("message_update", (event, ctx) => {
		latestCtx = ctx;
		ensureFooter(ctx);
		if (!current) return;

		const ev = event.assistantMessageEvent;
		if (ev.type !== "text_delta" && ev.type !== "thinking_delta" && ev.type !== "toolcall_delta") return;
		if (current.firstDeltaTs === undefined) current.firstDeltaTs = nowMs();
	});

	pi.on("message_end", (event, ctx) => {
		latestCtx = ctx;
		if (event.message.role !== "assistant" || !current) return;
		const usage = (event.message as AssistantMessage).usage;
		if (!usage) {
			current = undefined;
			lastRate = undefined;
			scheduleRender();
			return;
		}
		const endTs = nowMs();
		const { startTs, firstDeltaTs } = current;
		current = undefined;
		// Decode window: first stream delta → end. No deltas → full wall span from start.
		lastRate = computeTokenRate(usage.output, startTs, endTs, firstDeltaTs);
		scheduleRender();
	});
}
