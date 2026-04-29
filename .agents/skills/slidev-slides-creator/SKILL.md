---
name: slidev-slides-creator
description: Creates effective Slidev presentations by analyzing documentation, running parallel agents for each section, and synthesizing slide proposals. Use when creating developer presentations, technical slides, or when the user mentions Slidev, slide decks, presentations, or wants to convert content into slides with code highlighting, animations, and interactive elements.
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: Aziz
  version: "1.0"
---

# Slidev Slides Creator

Creates professional, interactive Slidev presentations optimized for technical content and developer audiences.

## When To Use

- User asks to create slides or a presentation
- User mentions Slidev, slide decks, or markdown presentations
- User wants to convert documentation/content into slides
- User needs technical presentations with code examples
- User requests presentations with animations, diagrams, or interactivity
- User wants to build developer-focused slide decks

## Core Workflow

### Phase 1: Gather Requirements

Before creating slides, establish:

1. **Topic/Purpose**: What is the presentation about? (tutorial, project demo, conference talk, documentation)
2. **Target Audience**: Developers, stakeholders, general audience?
3. **Duration**: Expected length (number of slides)
4. **Key Content**: Main points, code examples, diagrams needed
5. **Style Preference**: Minimal, feature-rich, specific theme?
6. **Export Needs**: PDF, SPA hosting, PPTX, or interactive web?

### Phase 2: Spawn Parallel Agents

Spawn specialized agents to analyze the documentation structure. Each agent processes a different domain:

**Agent 1: Structure & Flow Specialist**
- Analyze content hierarchy and logical flow
- Recommend overall slide structure (intro → content → conclusion)
- Suggest layouts for each slide type (see `references/layouts.md`)
- Determine navigation: TOC, section breaks, progress indicators

**Agent 2: Code & Technical Features Specialist**
- Identify all code snippets and technical content
- Recommend: Monaco editor, Magic Move, TwoSlash, line highlighting
- Plan code animations and progressive reveals
- Configure syntax highlighting for languages used

**Agent 3: Visual & Animation Designer**
- Design click animation sequences (v-click, v-clicks, v-after)
- Recommend transitions between slides
- Plan motion effects for key elements
- Suggest visual reveals for complex concepts

**Agent 4: Media & Diagrams Specialist**
- Identify diagram needs (Mermaid, PlantUML)
- Plan media embedding (YouTube, tweets, iframes)
- Recommend interactive components
- Suggest visual metaphors and illustrations

**Agent 5: Configuration & Export Specialist**
- Generate headmatter configuration
- Select theme (default, seriph, or custom)
- Configure fonts, colors, and styling
- Set up export options and hosting

Each agent reads their reference domain and returns recommendations.

### Phase 3: Synthesize Proposal

Combine all agent outputs into a structured proposal following the template in `references/proposal-template.md`. Include:

1. **Slide Structure**: Numbered list with titles and layouts
2. **Content Outline**: Key points per slide
3. **Feature Recommendations**: Which Slidev features to use
4. **Animation Plan**: Click sequences and transitions
5. **Configuration**: Headmatter with theme, fonts, exports
6. **File Organization**: Recommended directory structure

### Phase 4: Generate or Refine

Based on user preference, either:

- **A) Deliver Proposal**: Present recommendations for user review
- **B) Generate slides.md**: Create the actual presentation file

## Creating the slides.md File

When generating actual slides:

### File Structure

```markdown
---
# Headmatter configuration
theme: default
title: Presentation Title
# ... other options
---

# First Slide

Content here

---

# Second Slide

More content

<!-- 
Presenter notes
-->
```

### Essential Syntax Patterns

**Slide Separator**: `---` on its own line

**Frontmatter per slide**:
```yaml
---
layout: two-cols
clicks: 5
---
```

**Click Animations**:
```markdown
<v-click>Appears on first click</v-click>
<div v-click>Also appears on click</div>
<v-clicks>
- Item 1
- Item 2
</v-clicks>
```

**Code with Line Highlighting**:
````markdown
```ts {1|2-3|all}
function example() {
  console.log('step 1')
  return 'step 2'
}
```
````

**Two-Column Layout**:
```markdown
---
layout: two-cols
---

# Left Column

Content here

::right::

# Right Column

More content
```

**Code Groups**:
````markdown
::code-group

```sh [npm]
npm install
```

```sh [pnpm]
pnpm install
```

::
````

### Common Headmatter Options

```yaml
---
theme: default          # or seriph, or local path
title: My Presentation
info: |
  ## Author
  My Name
fonts:
  sans: Roboto
  mono: Fira Code
aspectRatio: 16/9
canvasWidth: 980
lineNumbers: true       # show in code blocks
monaco: true            # enable editor
export:
  format: pdf
  withClicks: false
---
```

## Gotchas

- **Slidev requires Node.js >= 20.12.0** — check version before creating
- **v-click values**: Use strings for relative positions (`'+1'`, `'-1'`), numbers for absolute
- **Code highlighting**: Shiki is built-in, supports 100+ languages
- **Monaco editor**: Heavy feature, only enable when needed
- **Theme fonts**: Auto-imported from Google Fonts, specify in headmatter
- **Export with clicks**: Use `--with-clicks` CLI flag for step-by-step PDF
- **Presenter notes**: HTML comments `<!-- -->` at end of slide
- **TwoSlash**: Requires TypeScript; add `twoslash` to code block language
- **Magic Move**: Use 4 backticks `````md magic-move` for code morphing
- **Layouts cascade**: theme → addons → custom (last wins)
- **Draggable elements**: Position persists via `dragPos` frontmatter
- **Remote assets**: Set `remoteAssets: true` to download external images
- **Route aliases**: Define `routeAlias` in frontmatter for deep linking
- **Mermaid diagrams**: Require `mermaid` code block language
- **LaTeX**: Use `$...$` inline or `$$...$$` block, or dedicated code block
- **Component auto-import**: Components in `components/` folder auto-register
- **UnoCSS classes**: Use Tailwind-like classes directly in markdown

## Progressive Disclosure

For detailed reference material, agents should load:

- `references/layouts.md` — Built-in layouts guide (cached from https://sli.dev/builtin/layouts.md)
- `references/components.md` — Built-in components reference (cached from https://sli.dev/builtin/components.md)
- `references/features.md` — Key features overview (cached from https://sli.dev/features/ and https://sli.dev/guide/)
- `references/proposal-template.md` — Output template structure
- `references/slide-templates.md` — Ready-to-use slide patterns

These references contain specific syntax, props, and usage examples.

### When to Fetch from Source

Use inline references by default for speed and reliability. Fetch from sli.dev source URLs when:
- User mentions a feature not covered in cached references
- Documentation seems outdated (check source for recent additions)
- Need specific edge case or advanced configuration
- Working with brand-new Slidev features (< 30 days old)

Source URLs are listed at the top of each reference file.
