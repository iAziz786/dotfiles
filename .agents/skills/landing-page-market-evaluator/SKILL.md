---
name: landing-page-market-evaluator
description: Evaluate a product idea through deep user interviewing, parallel live market research, and bounded narrowing loops, then produce 3 landing page title and subtitle pairs optimized for willingness to pay. Use when the user wants to test a product idea, assess market demand, understand urgent buyer pain, compare existing solutions, identify who will pay, or generate landing page messaging grounded in research.
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: Aziz
  version: "1.0"
---

# Landing Page Market Evaluator

Turn a raw product idea into a concrete landing page messaging test grounded in buyer pain, market evidence, and commercial focus.

## When To Use

Activate this skill when the user:
- Wants to evaluate a product idea before building it
- Wants to know whether a problem is urgent enough that customers will pay
- Asks for market assessment, competitor analysis, or target customer identification
- Wants landing page messaging based on research rather than intuition
- Says things like "help me validate this idea", "assess this market", "what will work", "who will pay for this", or "give me landing page headlines"

## Required Inputs

Before starting, establish:
- The raw product idea in one or two sentences
- Any known target user, industry, or geography if the user already has one
- Any constraints on the deliverable, such as "titles only" or "keep it to 3 options"

If the user is vague, do not block on perfect context. Start the first interview pass and use that to surface the real unknowns.

## Core Workflow

Run this workflow in order. Do not jump straight to headlines.

1. Restate the idea internally as a testable commercial hypothesis.
2. Ask a first round of deep questions using the `question` tool.
3. Form provisional hypotheses about:
   - likely buyers
   - urgent pain events
   - willingness-to-pay triggers
   - why current solutions may fail
   - biggest unknowns
4. Run live market research by default using parallel agents.
5. Consolidate the research into confirmed signals, contradictions, and unresolved risks.
6. Ask a second round of narrower questions using the `question` tool.
7. Re-rank the market wedge and stop when one primary wedge clearly outranks the rest.
8. Produce exactly 3 landing page title and subtitle pairs unless the user explicitly asks for a different count.

## Interview Guidance

Use the `question` tool for structured interviewing. Ask non-obvious questions that expose commercial and technical risk, not generic discovery questions.

The first question round should probe:
- Who feels the pain first versus who approves budget
- What specific event makes the pain urgent enough to pay for
- How quickly the problem becomes expensive or politically visible
- What the customer currently uses and where it fails
- Whether the real need is speed, actionability, attribution, automation, trust, or governance
- What accuracy or precision is required for the product to be believable
- Which onboarding or security hurdles could block adoption
- What outcome would count as a buying signal

The second question round should only probe unresolved risks discovered from research, such as:
- Which ICP actually has authority and urgency
- Which claim is credible enough to lead with
- Which part of the product is differentiated enough to sell
- Which segment should be avoided even if the pain sounds real
- Which tradeoff is acceptable in version 1

Do not ask obvious filler questions like "who is the user?" unless the user has provided no usable context at all.

## Ralph Loop

Use a bounded Ralph loop for discovery convergence when the user is new to the market or unsure what is truly payable.

The loop is:

1. Interview
2. Form hypotheses
3. Research in parallel
4. Check contradictions and weak evidence
5. Ask sharper follow-up questions
6. Re-rank the wedge

Use this loop to reduce false confidence from shallow assumptions.

### Stop Criteria

Stop the loop when all of the following are true:
- One ICP clearly outranks the others
- One pain is clearly more urgent and payable than the alternatives
- The incumbent weakness is concrete, not hand-wavy
- The leading claim is believable and not too broad
- Remaining uncertainty would not change the landing page direction

### Loop Boundaries

- Default to 1 full loop plus 1 follow-up loop
- Do not exceed 2 loops unless the user explicitly asks for deeper iteration
- If uncertainty is still too high after 2 loops, say so and explain what decision or evidence is missing

## Parallel Research

When live research is enabled, do not do broad research serially in the main agent. Use parallel subagents with the `task` tool.

Launch parallel agents for at least these tracks:

1. Competitor landscape
   - Use an `explore` agent
   - Identify direct competitors, adjacent tools, and native alternatives
   - Extract positioning, pricing shape, actionability claims, freshness claims, and target personas

2. Buyer pain evidence
   - Use an `explore` agent
   - Find reviews, community threads, case studies, forum posts, and public complaints
   - Focus on urgent, repeated, expensive pain rather than generic interest

3. Incumbent weakness validation
   - Use an `explore` agent
   - Verify delays, attribution issues, onboarding burden, trust gaps, workflow weakness, or noisy alerting from direct sources where possible

4. ICP and willingness-to-pay synthesis
   - Use a `general` agent
   - Rank likely customer segments by urgency, budget authority, onboarding friction, and expected willingness to pay

Optional:

5. Dynamic-site verification
   - Use an `explore` or `general` agent only if needed
   - Use Playwright only when static fetching is insufficient for pricing pages, JS-rendered claims, or gated UI content

Ask each agent to return:
- top findings
- source-backed evidence
- contradictions or uncertainty
- implications for positioning

The main agent owns synthesis. Parallel agents gather evidence; they do not decide the final landing page messaging.

## Research Guidance

Research should answer these questions explicitly:
- What urgent problems exist in this space?
- How bad are current solutions at solving them?
- Which existing customers are most likely to pay to solve them?
- Which product claims are credible versus overclaimed?
- What will likely work and what will likely not work in the first landing page test?

Separate:
- vendor claims
- direct-source product limitations
- user-reported pain
- your synthesis and recommendation

Prefer:
- `websearch` for discovery and current landscape research
- `webfetch` for direct product pages, docs, pricing pages, and public evidence
- `task` for parallel evidence gathering and synthesis

Use Playwright only if needed. Do not use it by default.

## Narrowing Pass

After research, select one primary wedge and, if useful, one backup wedge.

The primary wedge should specify:
- the buyer
- the payable pain
- the incumbent failure
- the believable promise

Also state what not to target, especially:
- low-urgency segments
- low-budget segments
- broad category claims that weaken differentiation
- overclaims that the evidence cannot support

## Output Contract

Default final output:

1. Best wedge
   - 2 to 4 bullets only

2. Market takeaways
   - urgent problems
   - existing solution gaps
   - best target customer
   - what is likely to work
   - what is likely not to work

3. Final landing page options
   - Option 1: title + subtitle
   - Option 2: title + subtitle
   - Option 3: title + subtitle

Unless the user asks otherwise, keep the final response concise and commercially oriented.

## Defaults

- Live research is on by default
- Use parallel agents for research by default
- Use a bounded Ralph loop when the user's market understanding is weak or uncertain
- Final deliverable defaults to exactly 3 title and subtitle pairs
- GitHub discussion creation is out of scope for this skill unless explicitly requested in a separate task

## Gotchas

- Do not jump to messaging before interviewing and research
- Do not confuse interesting problems with payable problems
- Do not assume the loudest complaint is the budget-owning complaint
- Do not present broad category language like "better visibility" if the real paid wedge is incident urgency or actionability
- Do not let each parallel agent invent separate final messaging recommendations
- Do not overclaim "real-time" if the research only supports "near-real-time" or "minutes"
- Do not let the Ralph loop run indefinitely; stop after 2 loops unless the user explicitly asks for more
- Use Playwright only when static sources are insufficient, not as the default research tool
