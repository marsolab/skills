---
name: landing-page-breakdown
description: Comprehensive landing page design analysis for extracting typography, color palette, spacing systems, visual elements, and conversion optimization insights. Use when a user provides a landing page URL for design analysis, wants to understand what makes a page effective, needs to extract design specifications, or wants to learn from high-converting landing pages.
---

# Landing Page Breakdown

Deep analysis of landing page design using screenshots and computed styles to extract actionable specifications, visual style characteristics, and conversion insights.

## Workflow Overview

1. **Capture** - Visit the page and save screenshots to `screenshots/` folder
2. **Describe** - Use screenshots to describe visual design in detail
3. **Extract** - Analyze design elements via JavaScript extraction
4. **Analyze** - Evaluate typography, colors, spacing, surfaces, blocks, and copy
5. **Report** - Generate `report.md` with findings and embedded screenshots

## Output Structure

```text
output/
├── report.md           # Final analysis report with embedded screenshots
└── screenshots/
    ├── 01-hero.png     # Above-fold hero section
    ├── 02-features.png # Features/benefits section
    ├── 03-social.png   # Social proof/testimonials
    ├── 04-pricing.png  # Pricing section (if present)
    ├── 05-cta.png      # Final CTA section
    ├── 06-footer.png   # Footer
    └── ...             # Additional sections as needed
```

## Step 1: Capture the Page

Navigate to the URL and systematically capture screenshots of each major section.

### Screenshot Capture Process

1. Navigate to the landing page URL
2. Create `screenshots/` folder for storing images
3. Take screenshot of hero/above-fold area, save as `screenshots/01-hero.png`
4. Scroll to each major section and capture:
   - Name screenshots sequentially: `02-features.png`, `03-testimonials.png`, etc.
   - Use descriptive suffixes matching section content
5. Capture any hover states, animations, or interactive elements
6. For long sections, capture multiple screenshots to show full content

### Screenshot Naming Convention

Use format: `NN-section-name.png` where NN is a two-digit sequence number. Examples: `01-hero.png`, `02-value-prop.png`, `03-features.png`, `04-how-it-works.png`, `05-testimonials.png`, `06-pricing.png`, `07-faq.png`, `08-final-cta.png`, `09-footer.png`.

## Step 2: Describe Design from Screenshots

After capturing screenshots, analyze each image to describe the visual design in detail. This visual description forms the foundation of the analysis.

### For Each Screenshot, Describe

**Layout and Composition**

- How elements are arranged (centered, asymmetric, grid-based)
- Visual hierarchy and what draws the eye first
- Use of whitespace and breathing room
- Section boundaries and transitions

**Visual Style Observations**

- Overall aesthetic (minimal, bold, playful, corporate, etc.)
- Shape language (rounded corners vs sharp edges, organic vs geometric)
- Depth and dimensionality (flat, subtle shadows, pronounced layering)
- Surface treatments visible (gradients, textures, glass effects, patterns)

**Color Impressions**

- Dominant colors and their emotional impact
- Color relationships and contrast levels
- Background treatment (solid, gradient, image, pattern)
- Accent color usage for emphasis

**Typography Observations**

- Heading style (bold, light, decorative, simple)
- Text density and readability
- Hierarchy between text elements
- Special text treatments (gradients, shadows, decorations)

**Component Observations**

- Button styles (shape, color, size, effects)
- Card and block designs (borders, shadows, backgrounds)
- Image treatments (rounded, masked, overlapping, framed)
- Icon style and usage

**Notable Design Decisions**

- Unique or distinctive elements
- Design patterns being used
- Consistency or intentional variations
- Mobile-friendliness indicators

## Step 3: Extract Design Elements

Execute JavaScript to extract computed styles from key elements.

### Typography Extraction

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

### Color Palette Extraction

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

### Spacing Analysis

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

### Image and Animation Detection

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

### Borders, Shadows, and Surface Treatments

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

### Block and Card Composition

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

### Layout Structure Analysis

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

## Step 4: Analyze Each Category

### 4.1 Typography Analysis

Evaluate the **primary font** used for headings, including font family and weight variations. Identify the **secondary font** used for body text and its typical weight. Assess **font pairing** for contrast, harmony, and readability between the chosen fonts. Determine the **type scale** ratio between heading sizes—common ratios are 1.25 (major second), 1.333 (perfect fourth), or 1.5 (perfect fifth). Evaluate **line heights** for readability, which should typically be 1.4-1.6 for body text. Note **letter spacing** patterns, which are often tight for headlines and normal for body copy.

### 4.2 Color Palette Analysis

Categorize colors by role. The **primary color** is the main brand color used for CTA buttons and key accents. The **secondary color** supports primary elements. **Background colors** include page background and section alternates for visual rhythm. **Text colors** span headlines, body text, and muted text variations. **Accent colors** appear on special elements, badges, alerts, and hover states. Assess **color contrast** for WCAG compliance, particularly between text and backgrounds.

### 4.3 Spacing System Analysis

Identify the **base unit** serving as the common spacing multiplier (typically 4px or 8px systems). Document **section spacing** that defines vertical rhythm between major blocks. Note **component spacing** for internal padding patterns. Analyze the **grid system** including column count, widths, and gutters. Evaluate **whitespace usage** around key elements to understand visual breathing room and focus areas.

### 4.4 Visual Elements Analysis

Document the **hero image or video** and the above-fold visual approach. Characterize the **photography style** as real photos, stock imagery, or custom photography. Analyze **illustrations** for style, complexity, and brand alignment. Note **icon style** (outline, solid, duotone) and consistency across the page. Catalog **animations** including scroll effects, micro-interactions, loading states, and hover animations. Assess **visual hierarchy** to understand how elements guide the viewer's eye through the content.

### 4.5 Visual Style and Surface Treatments

#### Borders

Analyze border usage patterns across the page. Document **border width** consistency, typically 1px for subtle definition or 2-3px for emphasis. Note **border style** preferences such as solid, dashed, or gradient borders. Identify **border color** choices and whether they use brand colors, neutral grays, or transparent borders with shadows instead. Assess **border radius** values to determine the shape language—0px creates sharp, modern edges; 4-8px suggests subtle softening; 12-24px indicates friendly, approachable design; and full radius (50%/9999px) creates pill shapes or circles.

#### Shadows and Depth

Document **shadow intensity** ranging from subtle (0 1px 2px) for minimal depth to dramatic (0 25px 50px) for floating elements. Note **shadow color**—pure black shadows feel harsh while tinted or brand-colored shadows appear more refined. Identify **shadow blur** and **spread** values to understand the depth system. Assess **layering strategy** to see how shadows create visual hierarchy between elements. Note any **inner shadows** used for inset effects on inputs or pressed states.

#### Surface Treatments

Catalog **background treatments** including solid colors, gradients (linear, radial, conic), patterns, noise/grain textures, glassmorphism (backdrop-filter blur), and mesh gradients. Note **opacity usage** for overlays, cards, and layered elements. Identify **backdrop filters** such as blur, saturation adjustments, or color overlays. Document any **texture or noise** applied to backgrounds for visual interest.

### 4.6 Block and Card Composition

#### Card Anatomy

Analyze how cards and content blocks are structured. Document the **card shell** including background, border, shadow, and radius values. Note **internal structure** such as image placement (top, side, background), content hierarchy, and action placement. Identify **padding patterns** for consistent internal spacing. Assess **aspect ratios** used for card images or the overall card shape.

#### Block Patterns

Identify common **layout patterns** used throughout the page. Note **feature blocks** showing icon/image, heading, description arrangement. Document **testimonial blocks** with quote, avatar, name, and title structure. Analyze **pricing cards** for tier differentiation through visual treatment. Assess **CTA blocks** for background treatment, padding, and button prominence.

#### Composition Techniques

Evaluate **alignment** consistency within and across blocks. Note **visual weight distribution** and how elements balance within containers. Identify **grouping strategies** using proximity, borders, or background colors. Document **hierarchy within blocks** showing how size, weight, and color establish importance.

### 4.7 Layout Patterns and Page Structure

#### Section Composition

Analyze how major page sections are structured. Document **section backgrounds** and how they alternate to create rhythm. Note **content width** constraints and maximum widths used. Identify **section padding** patterns for vertical rhythm. Assess **grid usage** including column counts and responsive behavior.

#### Visual Flow

Evaluate **reading patterns** the design encourages (F-pattern, Z-pattern, or single-column flow). Note **focal points** and how the eye is directed through the page. Identify **visual breaks** using whitespace, dividers, or background changes. Document **scroll triggers** and how content reveals as users navigate.

#### Responsive Considerations

Note **breakpoint indicators** visible in the design. Assess **mobile-first vs desktop-first** design philosophy. Identify elements likely to **stack or reflow** on smaller screens.

### 4.8 Overall Visual Style Description

Characterize the page's overall aesthetic using these dimensions:

**Design Era/Movement**: Identify the dominant style influence such as flat design, material design, neumorphism, glassmorphism, brutalism, minimalism, maximalism, retro/vintage, or corporate modern.

**Mood and Tone**: Describe the emotional quality conveyed—professional and trustworthy, playful and energetic, luxurious and premium, friendly and approachable, bold and innovative, calm and serene, or urgent and action-oriented.

**Shape Language**: Characterize the geometric vocabulary—predominantly rounded (friendly, soft), sharp and angular (modern, edgy), organic and fluid (natural, artistic), or mixed geometric (dynamic, varied).

**Density and Breathing Room**: Assess content density as spacious and airy, balanced and comfortable, or dense and information-rich.

**Color Temperature**: Determine if the palette feels warm, cool, neutral, or mixed.

**Visual Complexity**: Rate from minimal (few elements, lots of whitespace) to complex (many layers, textures, and details).

### 4.9 Copy Analysis

Evaluate the **headline formula** for structure, length, and emotional appeal. Assess the **value proposition** for clarity, uniqueness, and positioning. Review **subheadlines** for supporting messages and feature introductions. Analyze **CTA copy** for action words, urgency, and clarity. Document **social proof** elements including testimonials, logos, statistics, and trust badges. Note **microcopy** in form labels, button text, tooltips, and error states.

## Step 5: Conversion Analysis

### Conversion Elements Assessment

Evaluate whether the page demonstrates these high-converting characteristics: clear value proposition above the fold, single focused CTA with visual prominence, strategically placed social proof, emphasis on benefits over features, urgency or scarcity indicators when appropriate, trust signals such as security badges and guarantees, minimal navigation distractions, mobile-optimized design, fast perceived loading performance, and clear visual hierarchy that guides users toward conversion.

### Psychological Triggers

**Authority** includes expert endorsements, credentials, certifications, and media mentions. **Social proof** encompasses user counts, testimonials, client logos, case studies, and reviews. **Scarcity** involves limited availability messaging and exclusive access. **Urgency** covers time-sensitive offers and countdown timers. **Reciprocity** delivers free value before the ask through guides, tools, or trials. **Commitment** uses progressive engagement steps and micro-conversions.

## Step 6: Generate Report

Create the final `report.md` file following the **exact structure below**. Do not add, remove, or reorder sections. Fill in all placeholders with actual values.

### Report Requirements

**MANDATORY**: Every report must contain exactly these 14 sections in this order:

1. YAML Frontmatter
2. Title and Summary
3. At a Glance
4. Page Screenshots
5. Visual Style
6. Typography
7. Color Palette
8. Borders and Surfaces
9. Layout and Spacing
10. Visual Elements
11. Copy Analysis
12. Conversion Score
13. Key Takeaways
14. Design System Reference

### Strict Report Template

Copy this template exactly and fill in all `[PLACEHOLDER]` values:

````markdown
---
title: Landing Page Analysis
url: [FULL_URL]
analyzed: [YYYY-MM-DD]
overall_score: [X]/10
design_style: [STYLE_NAME]
primary_color: [#HEXCODE]
primary_font: [FONT_NAME]
border_radius: [X]px
target_audience: [AUDIENCE_TYPE]
key_strength: [ONE_SENTENCE]
key_improvement: [ONE_SENTENCE]
---

# Landing Page Analysis: [PAGE_TITLE]

> **Summary:** [ONE_SENTENCE_OVERVIEW]

---

## 1. At a Glance

| Attribute | Value |
|-----------|-------|
| URL | [FULL_URL] |
| Design Style | [STYLE_NAME] |
| Mood | [MOOD_DESCRIPTION] |
| Primary Color | [COLOR_NAME] `[#HEXCODE]` |
| Primary Font | [FONT_NAME] |
| Secondary Font | [FONT_NAME] |
| Border Radius | [X]px |
| Overall Score | **[X]/10** |

---

## 2. Page Screenshots

### 2.1 Hero
![Hero](screenshots/01-hero.png)

[2-3_SENTENCES_DESCRIBING_HERO_VISUAL_DESIGN]

### 2.2 Section 2
![Section 2](screenshots/02-[NAME].png)

[2-3_SENTENCES_DESCRIBING_THIS_SECTION]

### 2.3 Section 3
![Section 3](screenshots/03-[NAME].png)

[2-3_SENTENCES_DESCRIBING_THIS_SECTION]

### 2.4 Section 4
![Section 4](screenshots/04-[NAME].png)

[2-3_SENTENCES_DESCRIBING_THIS_SECTION]

### 2.5 Footer
![Footer](screenshots/[NN]-footer.png)

[2-3_SENTENCES_DESCRIBING_FOOTER]

---

## 3. Visual Style

| Dimension | Value |
|-----------|-------|
| Design Movement | [MOVEMENT_NAME] |
| Mood/Tone | [MOOD_DESCRIPTION] |
| Shape Language | [SHAPE_DESCRIPTION] |
| Visual Density | [DENSITY_LEVEL] |
| Color Temperature | [WARM/COOL/NEUTRAL] |
| Visual Complexity | [MINIMAL/MODERATE/COMPLEX] |

### Style Description

[PARAGRAPH_1: Overall visual impression and first reaction to the design]

[PARAGRAPH_2: How design choices support the brand/product positioning]

---

## 4. Typography

### 4.1 Font Stack

| Role | Font Name | Weights | Usage |
|------|-----------|---------|-------|
| Primary | [FONT] | [WEIGHTS] | Headlines, CTAs |
| Secondary | [FONT] | [WEIGHTS] | Body text, UI |

### 4.2 Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | [X]px | [X] | [X.X] |
| H2 | [X]px | [X] | [X.X] |
| H3 | [X]px | [X] | [X.X] |
| Body | [X]px | [X] | [X.X] |
| Small | [X]px | [X] | [X.X] |

### 4.3 Font Pairing Assessment

[2-3_SENTENCES_ON_HOW_FONTS_WORK_TOGETHER]

---

## 5. Color Palette

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| Primary | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |
| Secondary | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |
| Background | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |
| Surface | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |
| Text | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |
| Muted | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |
| Border | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |
| Accent | [#XXXXXX] | rgb([R],[G],[B]) | [USAGE] |

### Color Strategy

[2-3_SENTENCES_ON_COLOR_HARMONY_AND_EMOTIONAL_IMPACT]

---

## 6. Borders and Surfaces

### 6.1 Border System

| Element | Width | Radius | Color |
|---------|-------|--------|-------|
| Cards | [X]px | [X]px | [#XXXXXX] |
| Buttons | [X]px | [X]px | [#XXXXXX] |
| Inputs | [X]px | [X]px | [#XXXXXX] |

### 6.2 Shadow System

| Level | Value | Usage |
|-------|-------|-------|
| Subtle | [CSS_VALUE] | [USAGE] |
| Medium | [CSS_VALUE] | [USAGE] |
| Elevated | [CSS_VALUE] | [USAGE] |

### 6.3 Surface Treatments

[2-3_SENTENCES_ON_BACKGROUNDS_GRADIENTS_TEXTURES_EFFECTS]

---

## 7. Layout and Spacing

### 7.1 Grid System

| Property | Value |
|----------|-------|
| Container Width | [X]px |
| Columns | [X] |
| Gutter | [X]px |

### 7.2 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| Base Unit | [X]px | Foundation |
| Section Gap | [X]px | Between sections |
| Component Gap | [X]px | Between components |
| Element Gap | [X]px | Within components |

### 7.3 Page Sections

| # | Section | Background | Height |
|---|---------|------------|--------|
| 1 | Hero | [TREATMENT] | [~Xpx] |
| 2 | [NAME] | [TREATMENT] | [~Xpx] |
| 3 | [NAME] | [TREATMENT] | [~Xpx] |
| 4 | [NAME] | [TREATMENT] | [~Xpx] |
| 5 | Footer | [TREATMENT] | [~Xpx] |

---

## 8. Visual Elements

### 8.1 Imagery

| Aspect | Value |
|--------|-------|
| Type | [PHOTOGRAPHY/ILLUSTRATION/3D/MIXED] |
| Style | [STYLE_DESCRIPTION] |
| Treatment | [TREATMENT_DESCRIPTION] |

### 8.2 Icons

| Aspect | Value |
|--------|-------|
| Style | [OUTLINE/SOLID/DUOTONE/CUSTOM] |
| Size | [X]px |
| Color | [MONO/BRAND/MULTI] |

### 8.3 Animations

| Element | Animation | Duration |
|---------|-----------|----------|
| [ELEMENT] | [TYPE] | [Xs] |
| [ELEMENT] | [TYPE] | [Xs] |
| [ELEMENT] | [TYPE] | [Xs] |

---

## 9. Copy Analysis

### 9.1 Headlines

| Location | Text | Effectiveness |
|----------|------|---------------|
| Hero H1 | "[TEXT]" | [ASSESSMENT] |
| Section 2 | "[TEXT]" | [ASSESSMENT] |
| Section 3 | "[TEXT]" | [ASSESSMENT] |

### 9.2 CTAs

| Text | Location | Effectiveness |
|------|----------|---------------|
| "[TEXT]" | [LOCATION] | [ASSESSMENT] |
| "[TEXT]" | [LOCATION] | [ASSESSMENT] |

### 9.3 Value Proposition

[2-3_SENTENCES_ON_CLARITY_AND_POSITIONING]

### 9.4 Social Proof

| Type | Quantity | Placement |
|------|----------|-----------|
| [TYPE] | [X] | [LOCATION] |
| [TYPE] | [X] | [LOCATION] |

---

## 10. Conversion Score

**Overall: [X]/10**

| Category | Score | Note |
|----------|-------|------|
| Clarity | [X]/10 | [ONE_SENTENCE] |
| Visual Hierarchy | [X]/10 | [ONE_SENTENCE] |
| Trust Signals | [X]/10 | [ONE_SENTENCE] |
| CTA Effectiveness | [X]/10 | [ONE_SENTENCE] |
| Visual Cohesion | [X]/10 | [ONE_SENTENCE] |
| Mobile Readiness | [X]/10 | [ONE_SENTENCE] |

---

## 11. Key Takeaways

### ✅ Strengths

1. **[STRENGTH_1_TITLE]**: [EXPLANATION]
2. **[STRENGTH_2_TITLE]**: [EXPLANATION]
3. **[STRENGTH_3_TITLE]**: [EXPLANATION]

### 🔧 Improvements

1. **[IMPROVEMENT_1_TITLE]**: [EXPLANATION]
2. **[IMPROVEMENT_2_TITLE]**: [EXPLANATION]
3. **[IMPROVEMENT_3_TITLE]**: [EXPLANATION]

### 💡 Replicable Techniques

1. **[TECHNIQUE_1_TITLE]**: [EXPLANATION]
2. **[TECHNIQUE_2_TITLE]**: [EXPLANATION]
3. **[TECHNIQUE_3_TITLE]**: [EXPLANATION]

---

## 12. Design System Reference

```
COLORS
Primary:      [#XXXXXX]
Secondary:    [#XXXXXX]
Background:   [#XXXXXX]
Surface:      [#XXXXXX]
Text:         [#XXXXXX]
Muted:        [#XXXXXX]
Border:       [#XXXXXX]
Accent:       [#XXXXXX]

TYPOGRAPHY
Primary:      [FONT_NAME], [FALLBACK]
Secondary:    [FONT_NAME], [FALLBACK]
Base Size:    [X]px
Scale Ratio:  [X.XX]

BORDERS
Radius:       [X]px (cards), [X]px (buttons), [X]px (inputs)
Shadow:       [CSS_VALUE]

SPACING
Base Unit:    [X]px
Section:      [X]px
Component:    [X]px
Element:      [X]px

LAYOUT
Container:    [X]px
Columns:      [X]
Gutter:       [X]px
```

---

*Analysis generated on [YYYY-MM-DD]*
````

### Report Validation Checklist

Before finalizing `report.md`, verify:

- [ ] YAML frontmatter has all 11 fields filled
- [ ] All 12 main sections (numbered 1-12) are present
- [ ] All tables have no empty cells (use "N/A" or "None" if not applicable)
- [ ] All screenshots are referenced with correct paths
- [ ] All placeholder brackets `[...]` are replaced with actual values
- [ ] Exactly 3 items in Strengths, Improvements, and Techniques
- [ ] All scores are integers from 1-10
- [ ] All hex colors include the `#` prefix
- [ ] Design System Reference block has all values filled

## Analysis Tips

### Screenshot Best Practices

Capture screenshots at consistent viewport width (1440px recommended for desktop). Ensure each screenshot shows complete sections without cutting off content mid-element. For very long sections, capture multiple overlapping screenshots. Include hover states for buttons and interactive elements when they reveal important design details.

### Visual Description Guidelines

When describing screenshots, focus on what makes the design distinctive rather than obvious observations. Use comparative language to anchor descriptions—reference well-known design systems (Material Design, Apple HIG), popular frameworks (Tailwind defaults, Bootstrap), or recognizable brand aesthetics. Describe the emotional impression the design creates, not just the technical specifications.

### Extraction and Analysis

Compare extracted values against industry standards for context. Look for intentional repetition in spacing values, border radii, and color usage—consistency indicates a systematic approach. Note deviations from patterns, as these are often intentional for emphasis. Consider the target audience when evaluating design choices.

### Block Composition Analysis

Pay attention to the ratio of elements within cards—large image with small text suggests visual-first design, while text-heavy cards with small icons indicate information-first approach. Note whether blocks use consistent templates or vary intentionally to create hierarchy.

### Border and Surface Analysis

Look for the absence of visible borders as much as the presence—many modern designs rely on shadows, background color differences, or whitespace alone to define boundaries. Glassmorphism and neumorphism effects are particularly important to identify as they significantly characterize the visual style.

### Report Generation Rules

**CRITICAL**: Follow the exact report template structure. Do not deviate from the section order or table formats.

1. Save all screenshots to `screenshots/` folder BEFORE writing the report
2. Use exact section numbers (1-12) as shown in template
3. Fill ALL table cells—use "N/A", "None", or "0" if not applicable
4. Replace ALL `[PLACEHOLDER]` text with actual values
5. Keep exactly 3 items in Strengths, Improvements, and Techniques lists
6. Use integers 1-10 for all scores
7. Include `#` prefix for all hex color values
8. Match screenshot filenames exactly in markdown references
9. Run the validation checklist before finalizing
