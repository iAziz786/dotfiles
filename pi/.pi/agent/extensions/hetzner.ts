/**
 * Hetzner Inference API provider (https://experiments.hetzner.com/docs/inference)
 *
 * Free while experimental. OpenAI-compatible REST API:
 *   baseUrl: https://inference.hetzner.com/api/v1
 *   auth:    Bearer $HETZNER_INFERENCE_TOKEN
 *
 * All four models are MoE and emit `reasoning` content; the API ignores
 * unknown request fields (vLLM-style), so `thinkingFormat: "deepseek"`
 * (`thinking: {type: "enabled"}` + `reasoning_effort`) is a safe best-effort
 * thinking control for all of them.
 *
 * Rate limits (per key): 10M input / 200k output tokens per 60s -> HTTP 429.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const ZERO_COST = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 };

export default function (pi: ExtensionAPI) {
	pi.registerProvider("hetzner", {
		name: "Hetzner Inference",
		baseUrl: "https://inference.hetzner.com/api/v1",
		apiKey: "$HETZNER_INFERENCE_TOKEN",
		api: "openai-completions",
		models: [
			{
				id: "DeepSeek-V4-Flash-0731",
				name: "DeepSeek V4 Flash",
				reasoning: true,
				input: ["text"],
				cost: ZERO_COST,
				contextWindow: 512000,
				maxTokens: 16384,
				thinkingLevelMap: {
					off: "disabled",
					minimal: "low",
					low: "low",
					medium: "medium",
					high: "high",
					xhigh: "max",
					max: "max",
				},
				compat: {
					thinkingFormat: "deepseek",
					maxTokensField: "max_tokens",
				},
			},
			{
				id: "GLM-5.2-NVFP4",
				name: "GLM 5.2 NVFP4",
				reasoning: true,
				input: ["text"],
				cost: ZERO_COST,
				contextWindow: 512000,
				maxTokens: 16384,
				compat: {
					thinkingFormat: "deepseek",
					maxTokensField: "max_tokens",
				},
			},
			{
				id: "Kimi-K2.7-Code",
				name: "Kimi K2.7 Code",
				reasoning: true,
				input: ["text", "image"],
				cost: ZERO_COST,
				contextWindow: 262144,
				maxTokens: 16384,
				compat: {
					thinkingFormat: "deepseek",
					maxTokensField: "max_tokens",
				},
			},
			{
				id: "Qwen/Qwen3.6-35B-A3B-FP8",
				name: "Qwen3.6 35B A3B FP8",
				reasoning: true,
				input: ["text", "image"],
				cost: ZERO_COST,
				contextWindow: 262144,
				maxTokens: 16384,
				compat: {
					thinkingFormat: "deepseek",
					maxTokensField: "max_tokens",
				},
			},
		],
	});
}
