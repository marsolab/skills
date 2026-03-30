# Swift Best Practices

## Code Organization

### File Structure
- One type per file (class, struct, enum, protocol)
- Group related extensions in the same file
- Use `// MARK: -` comments to organize code sections
- Order: properties → lifecycle → public methods → private methods

### Naming Conventions
- Types: `UpperCamelCase` (classes, structs, enums, protocols)
- Variables/functions: `lowerCamelCase`
- Constants: `lowerCamelCase` (not SCREAMING_SNAKE_CASE)
- Protocols describing capability: suffix with `-able`, `-ing` (e.g., `Equatable`, `Coding`)
- Boolean variables: use `is`, `has`, `should` prefix (e.g., `isEnabled`, `hasContent`)

## Type Safety & Optionals

### Prefer Value Types
- Use `struct` by default, `class` only when needed
- Classes for: reference semantics, inheritance, Objective-C interop, identity comparison
- Structs for: value semantics, immutability, protocol-oriented design

### Optional Handling
```swift
// Prefer optional binding over force unwrapping
if let user = optionalUser {
    print(user.name)
}

// Use guard for early returns
guard let user = optionalUser else { return }
print(user.name)

// Use nil coalescing for defaults
let name = optionalName ?? "Unknown"

// Never force unwrap (!) in production code except:
// - IBOutlets (storyboard-guaranteed)
// - After explicit nil check
```

### Type Inference
```swift
// Good: leverage type inference
let numbers = [1, 2, 3]
let name = "John"

// Explicit when clarity needed
let ratio: Double = 3 / 4  // Without type, would be Int
```

## Modern Swift Patterns

### Property Wrappers
```swift
@Published var isLoading = false
@State private var count = 0
@Environment(\.dismiss) private var dismiss
@AppStorage("userId") private var userId: String?
```

### Async/Await
```swift
// Prefer async/await over completion handlers
func fetchUser(id: String) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Use Task for background work
Task {
    await performWork()
}

// Use async let for concurrent operations
async let user = fetchUser(id: "123")
async let posts = fetchPosts(userId: "123")
let (userData, postsData) = try await (user, posts)
```

### Result Type
```swift
// Use Result for sync operations with potential failure
func parseJSON(_ data: Data) -> Result<User, Error> {
    do {
        let user = try JSONDecoder().decode(User.self, from: data)
        return .success(user)
    } catch {
        return .failure(error)
    }
}
```

## Error Handling

### Structured Error Types
```swift
enum NetworkError: Error {
    case invalidURL
    case noConnection
    case serverError(statusCode: Int)
    case decodingError(Error)
}

// Throw specific errors
throw NetworkError.serverError(statusCode: 500)

// Handle with pattern matching
do {
    try performOperation()
} catch NetworkError.noConnection {
    showOfflineMessage()
} catch NetworkError.serverError(let code) {
    showServerError(code: code)
} catch {
    showGenericError()
}
```

## Protocol-Oriented Programming

### Protocol Design
```swift
// Small, focused protocols
protocol Identifiable {
    var id: String { get }
}

// Protocol composition
typealias Entity = Identifiable & Codable

// Protocol extensions with default implementations
extension Collection {
    var isNotEmpty: Bool { !isEmpty }
}

// Protocol with associated types
protocol Repository {
    associatedtype Entity
    func fetch() async throws -> [Entity]
}
```

### Prefer Protocols Over Inheritance
```swift
// Instead of base classes
class BaseViewModel { /* shared code */ }

// Use protocols with extensions
protocol ViewModelProtocol {
    var isLoading: Bool { get set }
}

extension ViewModelProtocol {
    func showLoader() { isLoading = true }
}
```

## Memory Management

### Capture Lists
```swift
// Use [weak self] for escaping closures
service.fetch { [weak self] result in
    guard let self else { return }
    self.handleResult(result)
}

// Use [unowned self] only when guaranteed to exist
timer = Timer.scheduledTimer(withTimeInterval: 1.0) { [unowned self] _ in
    self.update()
}

// Capture specific values
let currentValue = value
Task { [currentValue] in
    await process(currentValue)
}
```

### Reference Cycles
```swift
// Avoid in closures, delegates, parent-child relationships
protocol DataSourceDelegate: AnyObject {
    func didUpdate()
}

class DataSource {
    weak var delegate: DataSourceDelegate?  // weak to avoid cycle
}
```

## Collections & Algorithms

### Prefer Higher-Order Functions
```swift
// Instead of loops
let evenNumbers = numbers.filter { $0 % 2 == 0 }
let doubled = numbers.map { $0 * 2 }
let sum = numbers.reduce(0, +)

// Combine operations
let result = numbers
    .filter { $0 > 10 }
    .map { $0 * 2 }
    .sorted()

// Use compactMap to filter nils
let validUsers = users.compactMap { $0.email }
```

### Efficient Collection Usage
```swift
// Use Set for uniqueness/fast lookup
let uniqueIds = Set(ids)
if uniqueIds.contains(searchId) { }

// Use Dictionary for key-value mapping
let userDict = Dictionary(uniqueKeysWithValues: users.map { ($0.id, $0) })

// Lazy operations for large collections
let filtered = largeArray.lazy.filter { expensive($0) }
```

## Code Quality

### Access Control
```swift
// Default to private, widen as needed
private var internalState: Int
fileprivate var crossFileAccess: String
internal var moduleLevel: Bool  // internal is default
public var apiLevel: String
open class SubclassableClass {}  // open for inheritance
```

### Avoid Force Unwrapping
```swift
// Never in production code
let value = optional!  // ❌

// Acceptable exceptions
@IBOutlet weak var label: UILabel!  // Interface Builder guarantee
let value = optional ?? defaultValue  // ✅
```

### Use Extensions for Organization
```swift
// Separate protocol conformance
extension User: Codable {}
extension User: Equatable {}

// Group related functionality
extension String {
    var isValidEmail: Bool { /* validation */ }
}

// Keep main declaration clean
struct User {
    let id: String
    let name: String
}
```

## Performance Considerations

### Copy-on-Write Optimization
```swift
// Structs use COW - efficient for large collections
var original = [1, 2, 3, 4, 5]
var copy = original  // No copy yet
copy.append(6)  // Now copies

// Be aware in performance-critical code
```

### Lazy Properties
```swift
// Expensive initialization, computed once
lazy var expensiveProperty: HeavyObject = {
    HeavyObject(withConfig: config)
}()

// Not thread-safe - use with caution in concurrent contexts
```

### String Interpolation
```swift
// Efficient string building
let message = "User \(name) has \(count) items"

// Avoid string concatenation in loops
var result = ""
for item in items {
    result += "\(item)\n"  // ❌ Creates new string each time
}

// Use joined or array
let result = items.map(String.init).joined(separator: "\n")  // ✅
```

## Testing Best Practices

### Testable Code Design
```swift
// Inject dependencies
class ViewModel {
    private let service: ServiceProtocol
    
    init(service: ServiceProtocol = ProductionService()) {
        self.service = service
    }
}

// Use protocols for mocking
protocol ServiceProtocol {
    func fetch() async throws -> [Item]
}

// Test with mock
class MockService: ServiceProtocol {
    var mockData: [Item] = []
    func fetch() async throws -> [Item] { mockData }
}
```

### XCTest Patterns
```swift
func testUserCreation() async throws {
    // Given
    let service = MockUserService()
    let viewModel = UserViewModel(service: service)
    
    // When
    try await viewModel.createUser(name: "John")
    
    // Then
    XCTAssertEqual(viewModel.users.count, 1)
    XCTAssertEqual(viewModel.users.first?.name, "John")
}
```

## Concurrency

### Actor Usage
```swift
// Use actors for mutable state shared across concurrency domains
actor Counter {
    private var value = 0
    
    func increment() {
        value += 1
    }
    
    func getValue() -> Int {
        value
    }
}

// Access requires await
let counter = Counter()
await counter.increment()
let value = await counter.getValue()
```

### MainActor for UI
```swift
// Ensure UI updates on main thread
@MainActor
class ViewModel: ObservableObject {
    @Published var data: [Item] = []
    
    func loadData() async {
        let items = await service.fetch()
        data = items  // Already on MainActor
    }
}

// Or annotate specific functions
nonisolated func backgroundWork() {
    // Can run on any thread
}
```

### Task Management
```swift
// Store tasks for cancellation
private var fetchTask: Task<Void, Never>?

func loadData() {
    fetchTask?.cancel()
    fetchTask = Task {
        await performFetch()
    }
}

// TaskGroup for multiple concurrent operations
await withTaskGroup(of: User.self) { group in
    for id in userIds {
        group.addTask { await fetchUser(id: id) }
    }
    for await user in group {
        users.append(user)
    }
}
```

## Documentation

### Code Comments
```swift
/// Fetches user data from the API
/// - Parameter id: The unique user identifier
/// - Returns: User object with populated data
/// - Throws: NetworkError if request fails
func fetchUser(id: String) async throws -> User {
    // Implementation
}

// Use /// for documentation
// Use // for implementation notes
// Avoid obvious comments: let count = 0 // initialize count to zero
```

### MARK Comments
```swift
// MARK: - Properties
private let service: Service

// MARK: - Lifecycle
override func viewDidLoad() { }

// MARK: - Public Methods
func configure() { }

// MARK: - Private Methods
private func setupUI() { }

// MARK: - Actions
@objc private func buttonTapped() { }
```
