---
name: apple-dev
description: Comprehensive macOS and iOS development expertise covering Swift best practices, SwiftUI design patterns, Human Interface Guidelines, Apple frameworks, and performance optimization. Use when developing native Apple applications, implementing SwiftUI interfaces, working with Apple frameworks (Foundation, UIKit, AppKit, Core Data, CloudKit, etc.), optimizing app performance, following HIG principles, or writing production-quality Swift code for iOS, macOS, watchOS, or tvOS platforms.
---

# Apple Development

Expert-level guidance for building native Apple applications with Swift and
SwiftUI, following Apple's best practices and Human Interface Guidelines.

## Core Capabilities

### 1. Swift Programming Excellence

Write idiomatic, performant Swift code following modern best practices:

- **Type Safety & Optionals**: Proper optional handling with `guard`, `if let`,
  nil coalescing; avoid force unwrapping
- **Value Types First**: Prefer `struct` over `class`; use classes for reference
  semantics and inheritance
- **Protocol-Oriented Programming**: Small focused protocols, protocol
  extensions with default implementations
- **Modern Swift**: async/await, property wrappers, Result type, Codable,
  Combine
- **Memory Management**: [weak self] in closures, avoid retain cycles, efficient
  resource usage
- **Code Organization**: Clear file structure, meaningful naming, access
  control, MARK comments

**When to consult references**: For detailed patterns, advanced techniques, or
specific language features, read `references/swift-best-practices.md`

### 2. SwiftUI Interface Development

Build modern, declarative user interfaces following SwiftUI patterns:

- **State Management**: @State, @Binding, @StateObject, @ObservedObject,
  @EnvironmentObject, @Environment
- **Observable Macro**: Modern @Observable pattern for iOS 17+ (no @Published
  needed)
- **MVVM Pattern**: Clean separation with ViewModels, proper data flow
- **View Composition**: Break complex views into focused, reusable components
- **Custom Modifiers**: Reusable styling through ViewModifier protocol
- **Navigation**: NavigationStack, sheets, alerts, confirmation dialogs
- **Lists & Performance**: LazyVStack, ForEach optimization, equatable views
- **Animations**: Implicit/explicit animations, transitions, matched geometry
  effects

**When to consult references**: For layout patterns, advanced state management,
or SwiftUI-specific techniques, read `references/swiftui-patterns.md`

### 3. Human Interface Guidelines Compliance

Design interfaces that feel native and follow Apple's design principles:

- **Platform Conventions**: iOS navigation patterns (tab bar, navigation bar),
  macOS window management
- **Typography**: SF Pro font hierarchy, Dynamic Type support, accessibility
- **Color**: System colors, semantic colors, dark mode support, sufficient
  contrast
- **Layout**: Safe areas, spacing system (4pt grid), standard margins, touch
  targets (44x44pt minimum)
- **Components**: Standard buttons, lists, forms, navigation, sheets, alerts
- **Accessibility**: VoiceOver labels, Dynamic Type, reduce motion, color
  contrast
- **Gestures**: Tap, swipe, long press, pinch, proper haptic feedback

**When to consult references**: For detailed HIG requirements, component
specifications, or platform-specific patterns, read
`references/human-interface-guidelines.md`

### 4. Apple Frameworks Mastery

Leverage the full Apple ecosystem with deep framework knowledge:

- **Foundation**: String, Date, FileManager, UserDefaults, Codable, URLSession
- **UIKit/AppKit**: View controllers, table views, collection views, Auto Layout
- **SwiftUI**: Declarative UI, state management, navigation, animations
- **Networking**: URLSession async/await, Codable JSON parsing, error handling
- **Data Persistence**: Core Data, SwiftData (iOS 17+), UserDefaults, file
  system
- **Concurrency**: async/await, Task, actors, MainActor, TaskGroup
- **Combine**: Publishers, operators, reactive programming
- **CloudKit**: Public/private databases, CKRecord CRUD operations
- **StoreKit**: In-app purchases, subscriptions, transaction handling
- **Core Location & MapKit**: Location services, mapping, annotations
- **HealthKit**: Health data queries, authorization, samples
- **AVFoundation**: Audio/video playback, camera capture

**When to consult references**: For framework APIs, code samples, or integration
patterns, read `references/apple-frameworks.md`

### 5. Performance Optimization

Build fast, efficient applications with optimal resource usage:

- **Launch Time**: Defer initialization, lazy properties, optimize bundle size
- **Memory Management**: Fix leaks, reduce footprint, image optimization,
  caching
- **CPU Optimization**: Background queues, efficient algorithms, lazy operations
- **Rendering**: Optimize view hierarchy, SwiftUI performance, Core Animation
- **Network**: Reduce data transfer, batch requests, caching, offline mode
- **Battery**: Minimize location updates, efficient background tasks
- **Database**: Core Data batch operations, indexes, efficient queries
- **Profiling**: Instruments (Time Profiler, Allocations, Leaks), MetricKit

**When to consult references**: For optimization techniques, profiling
workflows, or specific performance patterns, read
`references/performance-optimization.md`

## Development Workflow

### Starting a New Project

1. **Choose Architecture**: SwiftUI-first for new apps, UIKit for legacy or
  specific requirements
1. **Set Up Structure**: MVVM for SwiftUI, MVC or VIPER for UIKit
1. **Configure Project**:
    - Enable Swift strict concurrency checking
    - Set deployment target appropriately
    - Configure code signing
1. **Follow Conventions**: File per type, MARK comments, proper access control
1. **Start with HIG**: Design following platform patterns before implementing

### Writing Code

1. **Reference Appropriate Documentation**: Consult skill references for
  detailed guidance
1. **Follow Swift Best Practices**: Type safety, optionals, protocol-oriented
  design
1. **Use Modern APIs**: async/await, @Observable (iOS 17+), SwiftUI when
  possible
1. **Test on Real Devices**: Simulators don't catch all issues
1. **Profile Early**: Use Instruments to identify bottlenecks

### Code Review Checklist

- [ ] Follows Swift style guidelines (naming, structure, access control)
- [ ] No force unwrapping (!) except in justified cases
- [ ] Proper memory management (no retain cycles, weak references where needed)
- [ ] UI updates on main thread (@MainActor or DispatchQueue.main)
- [ ] Error handling with proper Error types
- [ ] Accessibility labels and hints where appropriate
- [ ] Dynamic Type support for text
- [ ] Dark mode compatibility tested
- [ ] HIG compliance (spacing, colors, components)
- [ ] Performance profiled (no obvious leaks or slow operations)

## Common Patterns

### SwiftUI View with ViewModel

```swift
@MainActor
class UserViewModel: ObservableObject {
    @Published private(set) var users: [User] = []
    @Published private(set) var isLoading = false

    private let service: UserServiceProtocol

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }

    func loadUsers() async {
        isLoading = true
        do {
            users = try await service.fetchUsers()
        } catch {
            // Handle error
        }
        isLoading = false
    }
}

struct UsersView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else {
                List(viewModel.users) { user in
                    UserRow(user: user)
                }
            }
        }
        .task {
            await viewModel.loadUsers()
        }
    }
}
```

### Network Request with async/await

```swift
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        throw NetworkError.serverError
    }

    return try JSONDecoder().decode(User.self, from: data)
}
```

### Observable Model (iOS 17+)

```swift
@Observable
class ViewModel {
    var items: [Item] = []
    var isLoading = false

    func loadItems() async {
        isLoading = true
        items = await fetchItems()
        isLoading = false
    }
}

// In SwiftUI - automatically observes changes
struct ContentView: View {
    let viewModel = ViewModel()

    var body: some View {
        List(viewModel.items) { item in
            Text(item.name)
        }
    }
}
```

## Platform-Specific Considerations

### iOS

- Support multiple screen sizes (iPhone SE to Pro Max)
- Handle Dynamic Island on iPhone 14 Pro+
- Safe area insets for notch/home indicator
- Tab bar for 3-5 top-level sections
- Pull-to-refresh for content updates

### macOS

- Menu bar with standard menus (App, File, Edit, View, Window, Help)
- Window management (resize, minimize, maximize)
- Keyboard shortcuts for all actions
- Toolbar customization
- Right-click context menus

### iPad

- Support Split View and Slide Over multitasking
- Adapt layout for different sizes
- Keyboard shortcuts
- Pointer/trackpad support
- Drag and drop between apps

### watchOS

- Glanceable information
- Large touch targets (full screen width)
- Digital Crown for scrolling
- Minimal text input

### tvOS

- Focus-based navigation (Siri Remote)
- 10-foot viewing distance
- Large, clear text and images
- No touch interaction

## Accessibility

Always implement:

- VoiceOver labels for images and controls
- Accessibility hints for complex interactions
- Dynamic Type support for all text
- Minimum 4.5:1 contrast for text
- Reduce Motion support for animations
- Keyboard navigation support (macOS)

## Testing

- Unit tests for ViewModels and business logic
- UI tests for critical user flows
- Test on multiple devices and screen sizes
- Test in both light and dark mode
- Test with Dynamic Type at various sizes
- Test with VoiceOver enabled
- Profile with Instruments before release

## Resources

This skill includes comprehensive reference documentation:

### references/swift-best-practices.md

Complete Swift programming best practices covering code organization, type
safety, optionals, protocol-oriented programming, modern Swift features, memory
management, concurrency, and testing patterns.

### references/swiftui-patterns.md

SwiftUI design patterns including view composition, state management, MVVM
architecture, layout techniques, navigation patterns, animations, performance
optimization, and accessibility.

### references/human-interface-guidelines.md

Apple's Human Interface Guidelines covering design principles, platform
conventions, typography, color, layout, components, accessibility, gestures, and
platform-specific patterns for iOS, macOS, iPad, watchOS, and tvOS.

### references/apple-frameworks.md

Comprehensive reference for Apple frameworks including Foundation, UIKit,
AppKit, networking, Core Data, SwiftData, Combine, CloudKit, StoreKit, Core
Location, MapKit, HealthKit, AVFoundation, and Core Animation.

### references/performance-optimization.md

Performance optimization techniques covering app launch, memory management, CPU
optimization, rendering, networking, battery efficiency, database performance,
profiling with Instruments, and testing.
