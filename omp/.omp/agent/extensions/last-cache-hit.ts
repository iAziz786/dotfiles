import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent/extensibility/extensions";

// Publishes the last-request prompt-cache hit ratio to the status line:
// cacheRead / (cacheRead + cacheWrite + input), rendered by the "status" segment.

type Snapshot = {
	pct: number | null;
};

const snap: Snapshot = {
	pct: null,
};

export default function (pi: ExtensionAPI): void {
	pi.on("turn_end", (event, ctx) => {
		const msg = event.message;
		if (msg.role !== "assistant") return;
		const u = msg.usage;
		const denom = u.input + u.cacheRead + u.cacheWrite;
		snap.pct = denom > 0 ? (u.cacheRead / denom) * 100 : null;
		ctx.ui.setStatus("last-cache-hit", `L:${snap.pct === null ? "—" : snap.pct.toFixed(1)}%`);
	});
}
