# SwiftUI Design Patterns

## View Architecture

### View Composition
```swift
// Break down complex views into smaller components
struct ProfileView: View {
    var body: some View {
        VStack {
            ProfileHeaderView()
            ProfileStatsView()
            ProfileBioView()
        }
    }
}

// Each component is focused and reusable
struct ProfileHeaderView: View {
    var body: some View {
        HStack {
            Image(systemName: "person.circle.fill")
            Text("John Doe")
        }
    }
}
```

### View Modifiers
```swift
// Create custom view modifiers for reusable styling
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(Color.white)
            .cornerRadius(12)
            .shadow(radius: 4)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardStyle())
    }
}

// Usage
Text("Hello").cardStyle()
```

### PreferenceKey for Child-to-Parent Communication
```swift
struct HeightPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = max(value, nextValue())
    }
}

struct ChildView: View {
    var body: some View {
        Text("Content")
            .background(GeometryReader { geo in
                Color.clear.preference(
                    key: HeightPreferenceKey.self,
                    value: geo.size.height
                )
            })
    }
}

struct ParentView: View {
    @State private var height: CGFloat = 0
    
    var body: some View {
        ChildView()
            .onPreferenceChange(HeightPreferenceKey.self) { value in
                height = value
            }
    }
}
```

## State Management

### Property Wrappers

#### @State
```swift
// For simple local state in a view
struct CounterView: View {
    @State private var count = 0
    
    var body: some View {
        Button("Count: \(count)") {
            count += 1
        }
    }
}
// Use private for @State to prevent external modification
```

#### @Binding
```swift
// For two-way data flow between parent and child
struct ToggleView: View {
    @Binding var isOn: Bool
    
    var body: some View {
        Toggle("Setting", isOn: $isOn)
    }
}

struct ParentView: View {
    @State private var setting = false
    
    var body: some View {
        ToggleView(isOn: $setting)
    }
}
```

#### @StateObject & @ObservedObject
```swift
// @StateObject: View owns the object lifecycle
struct RootView: View {
    @StateObject private var viewModel = ViewModel()
    
    var body: some View {
        ContentView(viewModel: viewModel)
    }
}

// @ObservedObject: Object is passed in, view doesn't own it
struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        Text(viewModel.message)
    }
}
```

#### @EnvironmentObject
```swift
// For dependency injection across view hierarchy
class AppState: ObservableObject {
    @Published var user: User?
}

@main
struct MyApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

struct DeepChildView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Text(appState.user?.name ?? "Guest")
    }
}
```

#### @Environment
```swift
// For system environment values
struct ThemedView: View {
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.dismiss) var dismiss
    @Environment(\.openURL) var openURL
    
    var body: some View {
        Button("Open Website") {
            openURL(URL(string: "https://example.com")!)
        }
        .foregroundColor(colorScheme == .dark ? .white : .black)
    }
}

// Custom environment values
private struct ThemeKey: EnvironmentKey {
    static let defaultValue = Theme.default
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

extension View {
    func theme(_ theme: Theme) -> some View {
        environment(\.theme, theme)
    }
}
```

### Observable Macro (iOS 17+)
```swift
// Modern observation without @Published
@Observable
class ViewModel {
    var items: [Item] = []
    var isLoading = false
    
    func loadItems() async {
        isLoading = true
        items = await service.fetch()
        isLoading = false
    }
}

struct ContentView: View {
    let viewModel = ViewModel()
    
    var body: some View {
        // Automatically observes changes to used properties
        List(viewModel.items) { item in
            Text(item.name)
        }
    }
}
```

## MVVM Pattern

### ViewModel Design
```swift
@MainActor
class UserViewModel: ObservableObject {
    @Published private(set) var users: [User] = []
    @Published private(set) var isLoading = false
    @Published var errorMessage: String?
    
    private let service: UserServiceProtocol
    
    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }
    
    func loadUsers() async {
        isLoading = true
        errorMessage = nil
        
        do {
            users = try await service.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
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
                    Text(user.name)
                }
            }
        }
        .task {
            await viewModel.loadUsers()
        }
        .alert("Error", presenting: $viewModel.errorMessage) { _ in
            Button("OK") { viewModel.errorMessage = nil }
        } message: { message in
            Text(message)
        }
    }
}
```

## Layout

### Stacks
```swift
// VStack: vertical arrangement
VStack(alignment: .leading, spacing: 16) {
    Text("Title")
    Text("Subtitle")
}

// HStack: horizontal arrangement
HStack(alignment: .center, spacing: 8) {
    Image(systemName: "star")
    Text("Featured")
}

// ZStack: depth/overlapping
ZStack(alignment: .topTrailing) {
    Image("background")
    Badge()
}
```

### Spacing & Padding
```swift
// Spacing between elements
VStack(spacing: 20) { }

// Padding around element
Text("Hello").padding()
Text("Hello").padding(.horizontal, 24)
Text("Hello").padding(.top, 16)

// Multiple paddings
Text("Hello")
    .padding(.horizontal, 20)
    .padding(.vertical, 10)
```

### Frames
```swift
// Fixed size
Rectangle().frame(width: 100, height: 100)

// Flexible sizing
Text("Hello")
    .frame(maxWidth: .infinity)  // Expand to fill available width
    .frame(height: 44)  // Fixed height

// Minimum and maximum
Text("Hello")
    .frame(minWidth: 100, maxWidth: 300)
    .frame(minHeight: 44, maxHeight: 100)
```

### GeometryReader
```swift
// Access parent size and position
GeometryReader { geometry in
    Circle()
        .frame(width: geometry.size.width * 0.5)
        .position(
            x: geometry.size.width / 2,
            y: geometry.size.height / 2
        )
}

// Avoid overusing - can cause layout issues
// Only use when you truly need parent dimensions
```

### Grid (iOS 16+)
```swift
// Simple grid layout
Grid {
    GridRow {
        Text("Row 1, Col 1")
        Text("Row 1, Col 2")
    }
    GridRow {
        Text("Row 2, Col 1")
        Text("Row 2, Col 2")
    }
}

// LazyVGrid for large collections
LazyVGrid(columns: [
    GridItem(.adaptive(minimum: 100))
], spacing: 16) {
    ForEach(items) { item in
        ItemView(item: item)
    }
}
```

## Navigation

### NavigationStack (iOS 16+)
```swift
struct ContentView: View {
    @State private var path = NavigationPath()
    
    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: item) {
                    Text(item.name)
                }
            }
            .navigationDestination(for: Item.self) { item in
                DetailView(item: item)
            }
            .navigationTitle("Items")
        }
    }
}

// Programmatic navigation
path.append(item)  // Navigate forward
path.removeLast()  // Go back
path = NavigationPath()  // Pop to root
```

### Sheet & FullScreenCover
```swift
struct ContentView: View {
    @State private var showingSheet = false
    @State private var selectedItem: Item?
    
    var body: some View {
        Button("Show Sheet") {
            showingSheet = true
        }
        .sheet(isPresented: $showingSheet) {
            SheetView()
        }
        
        // Item-based presentation
        Button("Show Item") {
            selectedItem = item
        }
        .sheet(item: $selectedItem) { item in
            DetailView(item: item)
        }
        
        // Full screen
        .fullScreenCover(isPresented: $showingFullScreen) {
            FullScreenView()
        }
    }
}
```

### Alert & Confirmation Dialog
```swift
// Simple alert
.alert("Title", isPresented: $showAlert) {
    Button("OK") { }
    Button("Cancel", role: .cancel) { }
}

// Alert with data
.alert("Delete Item?", presenting: itemToDelete) { item in
    Button("Delete", role: .destructive) {
        delete(item)
    }
    Button("Cancel", role: .cancel) { }
}

// Confirmation dialog (action sheet)
.confirmationDialog("Choose Action", isPresented: $showDialog) {
    Button("Option 1") { }
    Button("Option 2") { }
    Button("Cancel", role: .cancel) { }
}
```

## Lists & Forms

### List Performance
```swift
// Use ForEach with id for dynamic content
List {
    ForEach(items, id: \.id) { item in
        ItemRow(item: item)
    }
}

// Identifiable is better
struct Item: Identifiable {
    let id: UUID
}

List(items) { item in
    ItemRow(item: item)
}

// Lazy loading for large lists
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```

### Swipe Actions
```swift
List {
    ForEach(items) { item in
        Text(item.name)
            .swipeActions(edge: .trailing) {
                Button(role: .destructive) {
                    delete(item)
                } label: {
                    Label("Delete", systemImage: "trash")
                }
            }
            .swipeActions(edge: .leading) {
                Button {
                    favorite(item)
                } label: {
                    Label("Favorite", systemImage: "star")
                }
                .tint(.yellow)
            }
    }
}
```

### Forms
```swift
Form {
    Section("Profile") {
        TextField("Name", text: $name)
        TextField("Email", text: $email)
    }
    
    Section("Preferences") {
        Toggle("Notifications", isOn: $notificationsEnabled)
        Picker("Theme", selection: $theme) {
            Text("Light").tag(Theme.light)
            Text("Dark").tag(Theme.dark)
        }
    }
    
    Section {
        Button("Save") {
            save()
        }
    }
}
```

## Animations

### Basic Animations
```swift
// Implicit animation
Text("Hello")
    .scaleEffect(isZoomed ? 1.5 : 1.0)
    .animation(.easeInOut, value: isZoomed)

// Explicit animation
withAnimation(.spring(response: 0.3)) {
    isExpanded.toggle()
}

// Custom timing
.animation(.easeInOut(duration: 0.5), value: offset)
```

### Transitions
```swift
if isShowing {
    Text("Hello")
        .transition(.scale.combined(with: .opacity))
}

// Custom transition
extension AnyTransition {
    static var slideAndFade: AnyTransition {
        .asymmetric(
            insertion: .move(edge: .trailing).combined(with: .opacity),
            removal: .move(edge: .leading).combined(with: .opacity)
        )
    }
}
```

### Matched Geometry Effect
```swift
@Namespace private var animation

if isExpanded {
    DetailView()
        .matchedGeometryEffect(id: "card", in: animation)
} else {
    ThumbnailView()
        .matchedGeometryEffect(id: "card", in: animation)
}
```

## Performance Optimization

### Lazy Loading
```swift
// Use LazyVStack/LazyHStack for long lists
ScrollView {
    LazyVStack {
        ForEach(0..<1000) { index in
            ExpensiveView(index: index)
        }
    }
}
// Views only created when scrolled into view
```

### EquatableView
```swift
// Prevent unnecessary re-renders
struct ExpensiveView: View, Equatable {
    let data: String
    
    var body: some View {
        // Complex rendering
        Text(data)
    }
    
    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.data == rhs.data
    }
}

// Usage
ExpensiveView(data: item.data)
    .equatable()
```

### Task Modifiers
```swift
// Async work tied to view lifecycle
.task {
    await loadData()
}

// Cancel when view disappears
.task(id: selectedCategory) {
    await loadData(for: selectedCategory)
}
// Cancels and restarts when selectedCategory changes
```

### Drawing Performance
```swift
// Rasterize complex content
ComplexView()
    .drawingGroup()  // Renders to offscreen buffer

// For static content
StaticContent()
    .drawingGroup(opaque: true, colorMode: .linear)
```

## Testing SwiftUI

### Preview Provider
```swift
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            ContentView()
                .preferredColorScheme(.light)
            
            ContentView()
                .preferredColorScheme(.dark)
            
            ContentView()
                .previewDevice("iPhone SE (3rd generation)")
        }
    }
}

// Macro syntax (iOS 17+)
#Preview {
    ContentView()
}

#Preview("Dark Mode") {
    ContentView()
        .preferredColorScheme(.dark)
}
```

### UI Testing
```swift
// Use accessibility identifiers
Text("Welcome")
    .accessibilityIdentifier("welcomeText")

// In tests
let app = XCUIApplication()
app.launch()
let welcomeText = app.staticTexts["welcomeText"]
XCTAssertTrue(welcomeText.exists)
```

## Custom Controls

### Button Styles
```swift
struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
    }
}

Button("Press Me") {
    action()
}
.buttonStyle(PrimaryButtonStyle())
```

### Progress View Styles
```swift
struct CustomProgressViewStyle: ProgressViewStyle {
    func makeBody(configuration: Configuration) -> some View {
        ZStack {
            Circle()
                .stroke(Color.gray.opacity(0.2), lineWidth: 8)
            Circle()
                .trim(from: 0, to: configuration.fractionCompleted ?? 0)
                .stroke(Color.blue, lineWidth: 8)
                .rotationEffect(.degrees(-90))
        }
    }
}
```

## Accessibility

### VoiceOver Support
```swift
Image(systemName: "star.fill")
    .accessibilityLabel("Favorite")
    .accessibilityHint("Double tap to add to favorites")

// Hide decorative elements
Image("decoration")
    .accessibilityHidden(true)

// Group related elements
HStack {
    Image(systemName: "person")
    Text("John Doe")
}
.accessibilityElement(children: .combine)
```

### Dynamic Type
```swift
// Respect user's text size preferences
Text("Hello")
    .font(.body)  // Scales automatically

// Custom fonts that scale
Text("Custom")
    .font(.custom("MyFont", size: 16, relativeTo: .body))

// Limit scaling
Text("Important")
    .dynamicTypeSize(.medium ... .xxxLarge)
```
