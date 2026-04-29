# Built-in Layouts Reference

> Source: https://sli.dev/builtin/layouts.md
> Fetched: 2026-04-18

Slidev provides 19 built-in layouts for structuring slides.

For latest updates or more examples, fetch from the source URL above.

## Presentation Structure

### `cover`
Title slide, first slide default.

```yaml
---
layout: cover
background: /cover-image.png
class: text-white
---

# My Presentation

Subtitle here
```

### `intro`
Introduction with title, description, author.

```yaml
---
layout: intro
---

# Introduction

About this presentation

By Author Name
```

### `section`
Marks new section/chapter.

```yaml
---
layout: section
---

# Section Title
```

### `end`
Final slide.

```yaml
---
layout: end
---

# Thank You

Questions?
```

### `statement`
Bold affirmation as main content.

```yaml
---
layout: statement
---

# "Quote or statement"
```

### `fact`
Prominent fact or data point.

```yaml
---
layout: fact
---

# 99%

Stat or key number
```

### `quote`
Quotation display.

```yaml
---
layout: quote
---

> "The quote text"

— Author Name
```

## Content Layouts

### `default`
Basic content layout (default for slides after first).

```yaml
---
layout: default
---

# Slide Title

Content here
```

### `center`
Centered content.

```yaml
---
layout: center
---

# Centered Title

Content in middle of slide
```

### `full`
Full-screen content, no padding.

```yaml
---
layout: full
---

# Full Screen

Content uses entire canvas
```

### `two-cols`
Two columns with separator.

```yaml
---
layout: two-cols
---

# Left Title

Left content here

::right::

# Right Title

Right content here
```

### `two-cols-header`
Header + two columns below.

```yaml
---
layout: two-cols-header
---

Header spanning both columns

::left::

# Left

Left content

::right::

# Right

Right content
```

## Media Layouts

### `image`
Full-screen image.

```yaml
---
layout: image
image: /path/to/image.png
backgroundSize: cover  # or contain, or specific values
---
```

### `image-left`
Image left, content right.

```yaml
---
layout: image-left
image: /path/to/image.png
class: my-content-class
---

# Title

Content appears on right side
```

### `image-right`
Image right, content left.

```yaml
---
layout: image-right
image: /path/to/image.png
class: my-content-class
---

# Title

Content appears on left side
```

### `iframe`
Embed webpage as main content.

```yaml
---
layout: iframe
url: https://example.com
---
```

### `iframe-left`
Webpage left, content right.

```yaml
---
layout: iframe-left
url: https://example.com
class: my-content-class
---

# Title

Content on right
```

### `iframe-right`
Webpage right, content left.

```yaml
---
layout: iframe-right
url: https://example.com
class: my-content-class
---

# Title

Content on left
```

## Utility Layouts

### `none`
No styling applied.

```yaml
---
layout: none
---

# Custom Layout

Build your own structure
```

## Layout Selection Guide

| Use Case | Recommended Layout |
|----------|-------------------|
| Title slide | `cover` |
| Introduction | `intro` |
| New section | `section` |
| Single concept | `default` or `center` |
| Code + explanation | `two-cols` |
| Screenshot demo | `image-right` or `image-left` |
| Live demo | `iframe` |
| Key statistic | `fact` |
| Famous quote | `quote` |
| Strong statement | `statement` |
| Comparison | `two-cols` or `two-cols-header` |
| Full visual | `full` or `image` |
| Custom styling | `none` |

## Layout Hierarchy

Layouts load in this order (later overrides earlier):
1. Built-in layouts (this reference)
2. Theme layouts
3. Addon layouts
4. Custom layouts in `layouts/` directory

Create custom layouts by adding `.vue` files to the `layouts/` folder.
