# Human Interface Guidelines (HIG)

## Design Principles

### Clarity

- Text is legible at all sizes
- Icons are precise and clear
- Decorations are subtle and appropriate
- Functionality is the priority

### Deference

- Content fills the screen while UI is unobtrusive
- Translucency and blur hint at more content
- Minimize bezels, gradients, and drop shadows

### Depth

- Visual layers and realistic motion convey hierarchy
- Touch and discoverability heighten delight
- Transitions provide context

## Platform Conventions

### iOS Specific

#### Navigation Patterns

- **Tab Bar**: 3-5 top-level sections, persistent across app
- **Navigation Bar**: Hierarchical navigation, back button, title
- **Search**: Top of scrollable content, tab bar icon, or navigation bar
- **Page Control**: Horizontal paging, centered at bottom

#### Common Controls

- **Buttons**: Filled (primary), Gray (secondary), Tinted, Plain
- **Segmented Controls**: Mutually exclusive options (2-5 items)
- **Sliders**: Choose value from continuous range
- **Steppers**: Increment/decrement by fixed amount
- **Switches**: Binary on/off for settings

#### Gestures

- **Tap**: Primary action, button press, select item
- **Drag**: Scroll, pan, rearrange items
- **Swipe**: Reveal actions, navigate, delete
- **Pinch**: Zoom in/out
- **Long Press**: Contextual menu, edit mode
- **Double Tap**: Zoom (maps, photos)

### macOS Specific

#### Window Management

- **Toolbars**: Common commands, customizable
- **Sidebars**: Navigation, filters, content organization
- **Inspector**: Object-specific settings on right
- **Title Bar**: Window title, traffic lights, inline controls

#### Menu Bar

- **Application Menu**: About, Preferences, Services, Quit
- **File Menu**: New, Open, Save, Print, Close
- **Edit Menu**: Undo, Cut, Copy, Paste, Select All
- **View Menu**: Display options, navigation
- **Window Menu**: Minimize, Zoom, window list
- **Help Menu**: Search, documentation

#### Keyboard

- Support full keyboard navigation
- Provide keyboard shortcuts for common actions
- Follow standard shortcuts (⌘C, ⌘V, ⌘S, etc.)
- Use ⌘ for app commands, ⌃ for text editing

## Typography

### iOS System Fonts

```swift
// San Francisco (SF Pro)
.font(.largeTitle)      // 34pt, bold
.font(.title)           // 28pt, regular
.font(.title2)          // 22pt, regular
.font(.title3)          // 20pt, regular
.font(.headline)        // 17pt, semibold
.font(.body)            // 17pt, regular
.font(.callout)         // 16pt, regular
.font(.subheadline)     // 15pt, regular
.font(.footnote)        // 13pt, regular
.font(.caption)         // 12pt, regular
.font(.caption2)        // 11pt, regular
```

### Text Hierarchy

- Use weight to establish hierarchy (not size alone)
- Limit number of font sizes (3-4 maximum)
- Ensure minimum 11pt for body text
- Support Dynamic Type for accessibility

### Line Height & Spacing

- Default line height: 1.2-1.5x font size
- Paragraph spacing: 0.5-1x line height
- Letter spacing: -0.5 to 1pt for headlines

## Color

### System Colors

```swift
// Semantic colors that adapt to light/dark mode
Color.primary           // Black/White
Color.secondary         // Gray
Color.accentColor       // User's accent preference

// UI Element Colors
Color(.systemBackground)
Color(.secondarySystemBackground)
Color(.tertiarySystemBackground)
Color(.systemGroupedBackground)

// Label Colors
Color(.label)           // Primary text
Color(.secondaryLabel)  // Secondary text
Color(.tertiaryLabel)   // Tertiary text
Color(.quaternaryLabel) // Watermarks

// Standard Colors
Color(.systemRed)
Color(.systemBlue)
Color(.systemGreen)
// etc.
```

### Color Usage

- **Avoid pure black (#000000)**: Use system colors
- **Test in both modes**: Light and dark appearance
- **Sufficient contrast**: 4.5:1 for text, 3:1 for UI
- **Don't rely on color alone**: Use icons or labels too
- **Accent color**: Single brand color, sparingly used

### Dark Mode

- Automatically support with system colors
- Test all states (normal, pressed, disabled)
- Elevate content with appropriate background levels
- Reduce white point with off-white colors

## Layout & Spacing

### Safe Areas

```swift
// Respect safe area insets
.padding(.horizontal)  // Standard padding
.edgesIgnoringSafeArea(.bottom)  // Extend if needed

// Safe area regions
.safeAreaInset(edge: .bottom) {
    Toolbar()
}
```

### Spacing System (iOS)

- **4pt grid**: Base unit for spacing
- **Small**: 8pt (1 grid unit)
- **Medium**: 16pt (2 grid units)
- **Large**: 24pt (3 grid units)
- **Extra Large**: 32pt (4 grid units)

### Standard Margins

- **iOS Margins**: 16pt/20pt horizontal (depending on device)
- **macOS Margins**: 20pt standard window margin
- **List Items**: 16pt vertical padding
- **Between Sections**: 24-32pt

### Touch Targets

- **Minimum**: 44x44pt (iOS), 24x24pt (macOS)
- **Recommended**: 48x48pt for primary actions
- **Spacing**: At least 8pt between targets

## Components

### Buttons

#### iOS Button Styles

```swift
// Filled - Primary actions
Button("Continue") { }
    .buttonStyle(.borderedProminent)

// Bordered - Secondary actions
Button("Cancel") { }
    .buttonStyle(.bordered)

// Borderless - Tertiary actions
Button("Learn More") { }
    .buttonStyle(.borderless)

// Plain - Text links
Button("Terms") { }
    .buttonStyle(.plain)
```

#### Button Content

- Use verbs describing action ("Save", "Send", "Delete")
- Title case for primary buttons
- Keep text short (1-2 words ideal)
- Include SF Symbol when appropriate

### Lists

#### List Styles

```swift
// Inset Grouped (iOS default)
List { }.listStyle(.insetGrouped)

// Sidebar (macOS, iPad)
List { }.listStyle(.sidebar)

// Plain (Simple lists)
List { }.listStyle(.plain)
```

#### Row Design

- **Leading Content**: Icon, avatar, or checkbox
- **Title**: Primary content (17pt, medium weight)
- **Subtitle**: Secondary info (15pt, regular)
- **Trailing Content**: Disclosure, detail, accessory
- **Spacing**: 12-16pt between title and subtitle

### Navigation

#### Navigation Bar

```swift
// Title styles
.navigationBarTitleDisplayMode(.large)  // 34pt, scrolls away
.navigationBarTitleDisplayMode(.inline)  // 17pt, fixed

// Toolbar items
.toolbar {
    ToolbarItem(placement: .navigationBarLeading) { }
    ToolbarItem(placement: .navigationBarTrailing) { }
}
```

#### Tab Bar

- 3-5 tabs maximum
- Always show labels
- Badge for notifications (numbers or dot)
- Selected state clearly indicated

### Sheets & Alerts

#### Sheet Presentation

```swift
// Standard sheet
.sheet(isPresented: $showSheet) { }

// Detents (size options)
.presentationDetents([.medium, .large])

// Drag indicator
.presentationDragIndicator(.visible)
```

#### Alert Design

- **Title**: Clear, specific (e.g., "Delete Photo?")
- **Message**: Brief explanation if needed
- **Buttons**: 1-2 options (max 3)
- **Destructive**: Red for dangerous actions
- **Cancel**: Always provide escape route

## Accessibility

### VoiceOver

```swift
// Descriptive labels
Image(systemName: "heart.fill")
    .accessibilityLabel("Favorite")

// Meaningful hints
.accessibilityHint("Double tap to add to favorites")

// Traits for context
.accessibilityAddTraits(.isButton)
.accessibilityAddTraits(.isHeader)

// Value for state
Toggle("Dark Mode", isOn: $darkMode)
    .accessibilityValue(darkMode ? "On" : "Off")
```

### Dynamic Type

```swift
// Support system font sizes
Text("Content").font(.body)

// Custom fonts that scale
.font(.custom("MyFont", size: 17, relativeTo: .body))

// Test at accessibility sizes
// Settings > Accessibility > Display & Text Size > Larger Text
```

### Color Contrast

- **Normal Text**: 4.5:1 minimum
- **Large Text**: 3:1 minimum (18pt+)
- **UI Components**: 3:1 minimum
- **Test in both modes**: Light and dark

### Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var animation: Animation {
    reduceMotion ? .none : .spring()
}
```

## Gestures & Interactions

### Touch Feedback

- **Visual**: Highlight on press
- **Haptic**: UIImpactFeedbackGenerator (light, medium, heavy)
- **Audio**: System sounds for specific actions

### Haptic Feedback

```swift
// Impact - UI element collision
UIImpactFeedbackGenerator(style: .medium).impactOccurred()

// Selection - Picking from list
UISelectionFeedbackGenerator().selectionChanged()

// Notification - Task completion/failure
UINotificationFeedbackGenerator().notificationOccurred(.success)
UINotificationFeedbackGenerator().notificationOccurred(.warning)
UINotificationFeedbackGenerator().notificationOccurred(.error)
```

### Context Menus

```swift
Text("Item")
    .contextMenu {
        Button("Copy", systemImage: "doc.on.doc") { }
        Button("Share", systemImage: "square.and.arrow.up") { }
        Button("Delete", systemImage: "trash", role: .destructive) { }
    }
```

## Platform-Specific Guidelines

### iPhone

- Support portrait and landscape (where appropriate)
- Handle Dynamic Island (iPhone 14 Pro+)
- Optimize for one-handed use
- Bottom-aligned primary actions

### iPad

- Support multitasking (Split View, Slide Over)
- Adapt to multiple window sizes
- Keyboard shortcuts for common actions
- Pointer support (hover states, cursor shapes)

### macOS

- Support menu bar with standard menus
- Window resizing (min/max sizes)
- Full keyboard navigation
- Right-click context menus
- Toolbar customization

### watchOS

- Design for glanceable information
- Large touch targets (entire screen width)
- Minimal text input (use Dictation, Scribble)
- Digital Crown for scrolling

### tvOS

- Focus-based navigation
- 10-foot viewing distance
- Siri Remote gestures
- No touch interaction

## Common Patterns

### Onboarding

- Show only when necessary
- 3-5 screens maximum
- Skip button always visible
- Demonstrate core value immediately

### Empty States

- Explain why empty ("No items yet")
- Provide action to add content
- Use illustration sparingly
- Be encouraging, not negative

### Loading States

- Show immediately for operations >0.5s
- Progress indication for operations >2s
- Allow cancellation when possible
- Provide context ("Loading your photos...")

### Error States

- Clear, human-readable messages
- Explain what happened and why
- Provide actionable solution
- Avoid technical jargon

### Settings

- Group related settings
- Use standard controls (Toggle, Picker)
- Clear labels without "Enable" prefix
- Provide hints for complex options
- Search for large setting lists

## App Architecture

### Information Architecture

- Flat over deep (2-3 levels maximum)
- Clear navigation path
- Consistent placement of controls
- Search for content-heavy apps

### Content Priority

- Most important content first
- Progressive disclosure for complexity
- Avoid overwhelming with options
- Clear visual hierarchy

### Consistency

- Use system components when possible
- Follow platform conventions
- Maintain internal consistency
- Predictable behavior across app
