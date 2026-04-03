---
name: skill-creator
description: Create a new agent skill (SKILL.md) in the .agents/skills/ folder. Use when the user wants to turn a workflow, template, or repeatable procedure into a reusable skill, asks to "create a skill", "write a skill", "extract this into a skill", or wants to package behavior so agents can invoke it on demand.
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: Aziz
  version: "1.0"
  skills_root: .agents/skills/
---

# Skill Creator

Create a new agent skill from source material (existing docs, conversation patterns, or manual workflows).

## When To Use

Activate this skill when the user:
- Asks to "create a skill" or "write a skill for X"
- Says "extract this into a skill" or "turn this into a reusable workflow"
- Wants to package a workflow so agents can invoke it on demand
- Wants to move content from AGENTS.md into a dedicated skill

## Before Creating (Reference Reading)

Read these from https://agentskills.io/ before creating any skill:

1. https://agentskills.io/what-are-skills.md — what skills are, progressive disclosure model
2. https://agentskills.io/specification.md — full format spec, frontmatter fields, directory structure
3. https://agentskills.io/skill-creation/best-practices.md — what to include, gotchas, templates
4. https://agentskills.io/skill-creation/optimizing-descriptions.md — how to write descriptions that trigger reliably

## Fitness Check

Not everything is a skill. A candidate only qualifies if it meets ALL THREE:

1. **Repeatable, multi-step workflow** — not just a rule or style guideline
2. **Defined output contract** — template, artifact, or deliverable
3. **Invoked on demand** — agent activates it, not always active

If the source material is ambient rules or guardrails, it should stay in AGENTS.md. State why it doesn't fit and stop.

## Gather Source Material

Before drafting, resolve:

- **Source**: Is it a section of AGENTS.md, a conversation pattern, or a repeated manual task?
- **Trigger**: When does an agent activate this? (user requests, task types)
- **Inputs/Outputs**: What data comes in, what artifact is produced?
- **Subdirectories needed**: Does it need `scripts/`, `references/`, or `assets/`? Only add if proven by prior manual runs.

## Name The Skill

Rules from the spec:

- Lowercase alphanumeric + hyphens only (`a-z0-9` and `-`)
- 1–64 characters
- No leading, trailing, or consecutive hyphens
- Must match the directory name exactly

Valid: `github-issue-spec`, `data-analysis`, `code-review`
Invalid: `PDF-Processing`, `-pdf`, `pdf--processing`, `MySkill`

## Write The Description

The description is the sole trigger mechanism. Write it following best practices:

- Use imperative phrasing: "Use when..."
- Describe user intent, not internal mechanics
- List explicit trigger phrases the user might say
- Stay under 1024 characters (hard limit from spec)

Good: "Extracts text and tables from PDF files, fills PDF forms. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction."
Poor: "Helps with PDFs."

## Required SKILL.md Structure

Create `.agents/skills/<skill-name>/SKILL.md` with this exact structure:

```markdown
---
name: <skill-name>
description: <trigger-optimized description under 1024 chars>
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: <author>
  version: "1.0"
---

# <Title>

## When To Use

## What This Skill Does (or Core Workflow)

## Gotchas
```

Recommended sections:
- **When To Use** — explicit trigger list
- **What This Skill Does** or **Core Workflow** — step-by-step instructions
- **Required Inputs** — what must be established before starting
- **Output Contract** — what the agent produces
- **Gotchas** — environment-specific facts that defy assumptions

Keep under 500 lines / 5000 tokens. Move overflow to `references/`.

## Optional Subdirectories

Only add if the skill explicitly needs them:

- `scripts/` — executable code the skill runs
- `references/` — docs loaded on demand (not in main context)
- `assets/` — templates, images, data files

Do not create empty directories. Add only when proven necessary.

## AGENTS.md Cleanup

If the skill was extracted from AGENTS.md:

1. Remove the full section from AGENTS.md
2. Replace with: `Use the \`<skill-name>\` skill when <trigger>.`
3. Never leave content in both places (violates DRY)

Example:
```markdown
## GitHub Issues

Use the `github-issue-spec` skill when creating GitHub issues as planning artifacts.
```

## Validation

Before finishing:

- [ ] Frontmatter includes `name` and `description`
- [ ] `name` matches the directory name exactly
- [ ] `description` is under 1024 characters and uses imperative phrasing
- [ ] SKILL.md is under 500 lines (or overflow moved to references/)
- [ ] Gotchas section includes environment-specific corrections
- [ ] If extracted from AGENTS.md, the original section is replaced with a skill reference

## Gotchas

- **Ambient rules are not skills** — leave always-on guidance in AGENTS.md
- **Don't create scripts prematurely** — only bundle scripts after the workflow has been run manually and the logic is proven
- **Descriptions are critical** — a skill that doesn't trigger is useless; optimize for the right balance of specificity
- **Size matters** — oversized skills hurt performance; use progressive disclosure (references/ for overflow)
- **Directory name must match skill name exactly** — case-sensitive on some filesystems
- **Never duplicate** — if a skill exists for this workflow, don't create another one
