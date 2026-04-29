# Built-in Components Reference

> Source: https://sli.dev/builtin/components.md
> Fetched: 2026-04-18

Slidev provides 20+ built-in Vue components for slides.

For latest updates or additional props, fetch from the source URL above.

## Navigation Components

### `Link`
Navigate to specific slides.

```markdown
<Link to="42">Go to slide 42</Link>
<Link to="42" title="Go to slide 42"/>
<Link to="solutions" title="Go to solutions"/>  <!-- uses routeAlias -->
```

Props:
- `to` (string|number): Slide number or route alias
- `title` (string): Display text

### `Toc`
Table of contents.

```markdown
<Toc />
<Toc :columns="2" :maxDepth="2"/>
<Toc mode="onlyCurrentTree"/>  <!-- shows active section only -->
```

Props:
- `columns` (number, default: 1): Number of columns
- `maxDepth` (number, default: ∞): Max heading level
- `minDepth` (number, default: 1): Min heading level
- `mode` ('all'|'onlyCurrentTree'|'onlySiblings'): Display mode

Hide slide from TOC: add `hideInToc: true` to frontmatter.

### `TitleRenderer`
Display title from another slide.

```markdown
<TitleRenderer no="5" />
```

Useful for creating section overview slides.

### `SlideCurrentNo` / `SlidesTotal`
Show slide numbers.

```markdown
Slide <SlideCurrentNo /> of <SlidesTotal />
```

## Animation Components

### `v-click` / `VClick`
Show element on click.

```markdown
<v-click>Appears on click 1</v-click>
<div v-click>Appears on click 1</div>
<div v-click="3">Appears on click 3</div>
<div v-click="'+2'">Appears 2 clicks after previous</div>
```

Hide after click:
```markdown
<div v-click.hide>Hidden after next click</div>
<v-click hide>Also hidden after next</v-click>
```

### `v-after` / `VAfter`
Show with previous click.

```markdown
<div v-click>First</div>
<div v-after>Appears with First</div>
```

### `v-clicks` / `VClicks`
Animate list items sequentially.

```markdown
<v-clicks>

- Item 1
- Item 2
- Item 3

</v-clicks>
```

Props:
- `depth` (number): Nested list depth to animate
- `every` (number): Items per click

### `v-switch` / `VSwitch`
Switch between slots on clicks.

```markdown
<v-switch>
  <template #1>Content for click 1</template>
  <template #2>Content for click 2</template>
  <template #5-7>Content for clicks 5-6</template>
</v-switch>
```

Props:
- `unmount` (boolean): Unmount previous slot when switching
- `transition` (string): Transition effect name

### `Transform`
Scale elements.

```markdown
<Transform :scale="0.5" origin="top center">
  <YourContent />
</Transform>
```

Props:
- `scale` (number): Scale factor
- `origin` (string): Transform origin

## Media Components

### `Tweet`
Embed tweet.

```markdown
<Tweet id="20" />
<Tweet id="20" :scale="1.5" conversation="none"/>
```

### `Youtube`
Embed YouTube video.

```markdown
<Youtube id="VIDEO_ID" />
<Youtube id="VIDEO_ID?start=120" />  <!-- start at 2:00 -->
```

### `SlidevVideo`
Embed local video.

```markdown
<SlidevVideo v-click autoplay controls>
  <source src="/video.mp4" type="video/mp4"/>
</SlidevVideo>
```

Props:
- `autoplay` (boolean|'once'): Auto-start video
- `controls` (boolean): Show controls
- `autoreset` ('slide'|'click'): Reset position on navigation

### `LightOrDark`
Different content per theme.

```markdown
<LightOrDark>
  <template #dark>
    
![Dark Image](/dark.png)

  </template>
  <template #light>
    
![Light Image](/light.png)

  </template>
</LightOrDark>
```

## Drawing Components

### `Arrow`
Draw arrow.

```markdown
<Arrow x1="10" y1="20" x2="100" y2="200" />
<Arrow x1="10" y1="20" x2="100" y2="200" width="4" color="red" two-way/>
```

Props:
- `x1`, `y1`, `x2`, `y2` (number): Coordinates
- `width` (number, default: 2): Line width
- `color` (string, default: 'currentColor'): Line color
- `two-way` (boolean): Bidirectional arrow

### `VDragArrow`
Draggable arrow.

```markdown
<VDragArrow v-drag="'arrow1'" x1="10" y1="20" x2="100" y2="200"/>
```

Position persists via `dragPos` frontmatter.

## Utility Components

### `RenderWhen`
Conditional rendering by context.

```markdown
<RenderWhen context="presenter">
  Only in presenter view
</RenderWhen>

<RenderWhen :context="['print', 'slide']">
  In print or slide mode
</RenderWhen>
```

Contexts: 'main', 'visible', 'print', 'slide', 'overview', 'presenter', 'previewNext'

### `PoweredBySlidev`
Credit badge.

```markdown
<PoweredBySlidev />
```

### `AutoFitText`
Auto-sizing text box.

```markdown
<AutoFitText :max="200" :min="100" modelValue="Dynamic text size"/>
```

## Component Auto-Import

Components are auto-imported from:
1. Built-in (listed above)
2. Current theme
3. Addons
4. `components/` directory

Create custom components by adding `.vue` files to `components/` folder.

## Usage Tips

- Use `<v-clicks>` for bullet points that should appear sequentially
- Combine `<v-click>` with code line highlighting for synchronized reveals
- `<Transform>` is great for zooming into diagrams
- `<LightOrDark>` ensures visibility in both themes
- `<RenderWhen>` helps hide presenter-only content from exports
