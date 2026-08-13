# Computed Style Extraction Scripts

Use these browser-side JavaScript snippets during Step 3 of the landing-page
breakdown workflow. Run them against the rendered page, retain representative
results, and use those results as evidence for the category analysis.

## Contents

- [Typography Extraction](#typography-extraction)
- [Color Palette Extraction](#color-palette-extraction)
- [Spacing Analysis](#spacing-analysis)
- [Image and Animation Detection](#image-and-animation-detection)
- [Borders, Shadows, and Surface Treatments](#borders-shadows-and-surface-treatments)
- [Block and Card Composition](#block-and-card-composition)
- [Layout Structure Analysis](#layout-structure-analysis)

## Typography Extraction

```javascript
const fonts = new Set();
const typography = [];
document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, a, button, span, li').forEach(el => {
  const style = getComputedStyle(el);
  fonts.add(style.fontFamily);
  typography.push({
    tag: el.tagName,
    text: el.textContent.slice(0, 50),
    fontFamily: style.fontFamily,
    fontSize: style.fontSize,
    fontWeight: style.fontWeight,
    lineHeight: style.lineHeight,
    letterSpacing: style.letterSpacing
  });
});
JSON.stringify({fonts: [...fonts], samples: typography.slice(0, 30)}, null, 2);
```

## Color Palette Extraction

```javascript
const colors = new Set();
document.querySelectorAll('*').forEach(el => {
  const style = getComputedStyle(el);
  [style.backgroundColor, style.color, style.borderColor].forEach(c => {
    if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') colors.add(c);
  });
});
[...colors].slice(0, 25);
```

## Spacing Analysis

```javascript
const sections = document.querySelectorAll('section, header, footer, main, [class*="section"], [class*="block"], [class*="container"]');
const spacing = [];
sections.forEach(el => {
  const style = getComputedStyle(el);
  spacing.push({
    element: el.className || el.tagName,
    padding: style.padding,
    margin: style.margin,
    gap: style.gap
  });
});
JSON.stringify(spacing, null, 2);
```

## Image and Animation Detection

```javascript
const visuals = {
  images: [...document.querySelectorAll('img')].map(img => ({
    src: img.src?.slice(0, 100),
    alt: img.alt,
    width: img.width,
    height: img.height
  })).slice(0, 15),
  videos: document.querySelectorAll('video').length,
  svgs: document.querySelectorAll('svg').length,
  animations: [...document.querySelectorAll('[class*="animate"], [class*="motion"], [class*="fade"], [class*="slide"]')].length
};
JSON.stringify(visuals, null, 2);
```

## Borders, Shadows, and Surface Treatments

```javascript
const surfaces = [];
document.querySelectorAll('div, section, article, aside, card, [class*="card"], [class*="box"], [class*="panel"], [class*="block"], button, input, a').forEach(el => {
  const style = getComputedStyle(el);
  const hasBorder = style.borderWidth !== '0px' && style.borderStyle !== 'none';
  const hasShadow = style.boxShadow !== 'none';
  const hasRadius = style.borderRadius !== '0px';
  if (hasBorder || hasShadow || hasRadius) {
    surfaces.push({
      element: el.className?.slice(0, 50) || el.tagName,
      borderWidth: style.borderWidth,
      borderStyle: style.borderStyle,
      borderColor: style.borderColor,
      borderRadius: style.borderRadius,
      boxShadow: style.boxShadow,
      background: style.background?.slice(0, 100),
      backdropFilter: style.backdropFilter
    });
  }
});
JSON.stringify(surfaces.slice(0, 25), null, 2);
```

## Block and Card Composition

```javascript
const blocks = [];
document.querySelectorAll('[class*="card"], [class*="box"], [class*="panel"], [class*="tile"], [class*="item"], [class*="feature"], [class*="benefit"], article').forEach(el => {
  const style = getComputedStyle(el);
  const children = el.children;
  blocks.push({
    element: el.className?.slice(0, 60) || el.tagName,
    width: style.width,
    height: style.height,
    display: style.display,
    flexDirection: style.flexDirection,
    alignItems: style.alignItems,
    justifyContent: style.justifyContent,
    gridTemplateColumns: style.gridTemplateColumns,
    childCount: children.length,
    childTypes: [...children].slice(0, 5).map(c => c.tagName)
  });
});
JSON.stringify(blocks.slice(0, 15), null, 2);
```

## Layout Structure Analysis

```javascript
const layout = {
  containers: [...document.querySelectorAll('[class*="container"], [class*="wrapper"], [class*="content"]')].map(el => ({
    class: el.className?.slice(0, 50),
    maxWidth: getComputedStyle(el).maxWidth,
    width: getComputedStyle(el).width,
    padding: getComputedStyle(el).padding
  })).slice(0, 10),
  grids: [...document.querySelectorAll('[class*="grid"], [style*="grid"]')].map(el => ({
    class: el.className?.slice(0, 50),
    gridTemplateColumns: getComputedStyle(el).gridTemplateColumns,
    gap: getComputedStyle(el).gap
  })).slice(0, 10),
  flexContainers: [...document.querySelectorAll('[class*="flex"], [style*="flex"]')].map(el => ({
    class: el.className?.slice(0, 50),
    flexDirection: getComputedStyle(el).flexDirection,
    gap: getComputedStyle(el).gap,
    flexWrap: getComputedStyle(el).flexWrap
  })).slice(0, 10)
};
JSON.stringify(layout, null, 2);
```
