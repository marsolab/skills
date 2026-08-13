# Strict Landing Page Report Template

Use this reference during Step 6 of the landing-page breakdown workflow.

Create the final `report.md` file following the exact structure below. Do not
add, remove, or reorder sections. Fill every placeholder with an actual value.

## Contents

- [Report Requirements](#report-requirements)
- [Template](#template)
- [Report Validation Checklist](#report-validation-checklist)

## Report Requirements

Every report must contain exactly these 14 sections in this order:

1. YAML Frontmatter
1. Title and Summary
1. At a Glance
1. Page Screenshots
1. Visual Style
1. Typography
1. Color Palette
1. Borders and Surfaces
1. Layout and Spacing
1. Visual Elements
1. Copy Analysis
1. Conversion Score
1. Key Takeaways
1. Design System Reference

## Template

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

```text
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

## Report Validation Checklist

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
