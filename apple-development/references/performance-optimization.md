# Performance Optimization

## App Launch Time

### Reduce Launch Time
```swift
// Defer non-critical initialization
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    
    // Critical setup only
    setupWindow()
    
    // Defer heavy work
    DispatchQueue.global(qos: .userInitiated).async {
        self.setupAnalytics()
        self.preloadData()
    }
    
    return true
}

// Lazy initialization
lazy var expensiveResource: HeavyObject = {
    HeavyObject()
}()

// Use static let for singletons
class Manager {
    static let shared = Manager()
    private init() {}
}
```

### Optimize App Bundle
- Remove unused resources and frameworks
- Use asset catalogs for images
- Compress images appropriately
- Use on-demand resources for rarely used content
- Enable bitcode for App Store optimization

### Reduce Binary Size
```swift
// Strip debug symbols in Release builds
// Build Settings:
// - Strip Debug Symbols During Copy: YES
// - Strip Swift Symbols: YES
// - Dead Code Stripping: YES

// Avoid unnecessary dependencies
// Use lightweight alternatives where possible
```

## Memory Management

### Identify Memory Leaks
```swift
// Use Instruments Memory Graph Debugger
// Profile > Leaks
// Profile > Allocations

// Common causes:
// 1. Strong reference cycles
class Parent {
    var child: Child?
}

class Child {
    weak var parent: Parent?  // Use weak to break cycle
}

// 2. Closures capturing self
service.fetch { [weak self] result in
    guard let self else { return }
    self.handle(result)
}

// 3. Timer retain cycles
timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
    self?.update()
}
```

### Reduce Memory Footprint
```swift
// Release resources when not needed
override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    imageCache.removeAllObjects()
    releaseCachedData()
}

// Use autoreleasepool for batch processing
func processManyImages() {
    for imageURL in imageURLs {
        autoreleasepool {
            let image = processImage(url: imageURL)
            save(image)
        }
    }
}

// Lazy loading for large collections
lazy var largeDataSet: [Item] = {
    loadLargeDataSet()
}()
```

### Image Optimization
```swift
// Downsample large images
func downsample(imageAt url: URL, to size: CGSize) -> UIImage? {
    let options = [
        kCGImageSourceCreateThumbnailWithTransform: true,
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        kCGImageSourceThumbnailMaxPixelSize: max(size.width, size.height)
    ] as CFDictionary
    
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateThumbnailAtIndex(source, 0, options) else {
        return nil
    }
    
    return UIImage(cgImage: image)
}

// Use image caching
let cache = NSCache<NSString, UIImage>()
cache.countLimit = 100
cache.totalCostLimit = 50 * 1024 * 1024  // 50MB

if let cachedImage = cache.object(forKey: key as NSString) {
    return cachedImage
} else {
    let image = loadImage()
    cache.setObject(image, forKey: key as NSString)
    return image
}
```

## CPU Optimization

### Reduce Main Thread Work
```swift
// Move expensive work off main thread
Task.detached(priority: .userInitiated) {
    let result = await performExpensiveCalculation()
    await MainActor.run {
        updateUI(with: result)
    }
}

// Use background queues
DispatchQueue.global(qos: .userInitiated).async {
    let data = self.processData()
    DispatchQueue.main.async {
        self.updateUI(data)
    }
}
```

### Optimize Algorithms
```swift
// Use appropriate data structures
// Array - sequential access, ordered
// Set - uniqueness, fast lookup O(1)
// Dictionary - key-value mapping, O(1) lookup

// Bad: O(n²)
for item in items {
    if otherItems.contains(item) {  // O(n) lookup in array
        // process
    }
}

// Good: O(n)
let itemSet = Set(otherItems)  // O(n) to create set
for item in items {
    if itemSet.contains(item) {  // O(1) lookup in set
        // process
    }
}

// Use lazy operations for large collections
let result = largeArray
    .lazy  // Prevents intermediate array creation
    .filter { $0 > 100 }
    .map { $0 * 2 }
    .first(where: { $0 > 500 })
```

### Avoid Premature Optimization
```swift
// Profile before optimizing
// Use Instruments > Time Profiler
// Identify actual bottlenecks, don't guess

// Measure performance
let start = CFAbsoluteTimeGetCurrent()
performOperation()
let elapsed = CFAbsoluteTimeGetCurrent() - start
print("Elapsed time: \(elapsed)s")
```

## Rendering Performance

### Optimize View Hierarchy
```swift
// Minimize view layers
// Flat > Deep hierarchy

// Bad: Unnecessary container views
VStack {
    VStack {
        VStack {
            Text("Content")
        }
    }
}

// Good: Flat structure
VStack {
    Text("Content")
}

// Reuse cells in lists
func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
    configure(cell, with: items[indexPath.row])
    return cell
}
```

### SwiftUI Performance
```swift
// Use equatable views to prevent unnecessary redraws
struct ItemView: View, Equatable {
    let item: Item
    
    var body: some View {
        Text(item.name)
    }
    
    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.item.id == rhs.item.id
    }
}

ItemView(item: item).equatable()

// Lazy loading for long lists
ScrollView {
    LazyVStack {  // Only creates views when visible
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}

// Offscreen rendering for complex views
ComplexView()
    .drawingGroup()  // Renders to offscreen buffer
```

### Core Animation
```swift
// Enable shouldRasterize for static content
layer.shouldRasterize = true
layer.rasterizationScale = UIScreen.main.scale

// Use opaque views when possible
view.isOpaque = true
view.backgroundColor = .white  // Not clear

// Avoid expensive blending
// Use .opacity modifier sparingly
// Prefer solid colors over gradients
```

## Network Optimization

### Reduce Data Transfer
```swift
// Request only needed fields
// Use pagination
struct PaginatedRequest {
    let page: Int
    let limit: Int = 20
}

// Cache responses
let config = URLSessionConfiguration.default
config.requestCachePolicy = .returnCacheDataElseLoad
config.urlCache = URLCache(
    memoryCapacity: 10 * 1024 * 1024,  // 10MB
    diskCapacity: 50 * 1024 * 1024      // 50MB
)

// Compress requests
var request = URLRequest(url: url)
request.setValue("gzip", forHTTPHeaderField: "Accept-Encoding")
```

### Optimize API Calls
```swift
// Batch requests
func fetchMultiple(ids: [String]) async throws -> [Item] {
    // Single request for multiple items
    let url = buildBatchURL(ids: ids)
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([Item].self, from: data)
}

// Debounce search queries
@Published var searchText = ""

$searchText
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .sink { text in
        performSearch(text)
    }

// Cancel in-flight requests
private var currentTask: Task<Void, Never>?

func search(query: String) {
    currentTask?.cancel()
    currentTask = Task {
        await performSearch(query)
    }
}
```

### Handle Offline Mode
```swift
// Check reachability
import Network

let monitor = NWPathMonitor()
monitor.pathUpdateHandler = { path in
    if path.status == .satisfied {
        print("Connected")
    } else {
        print("Offline")
    }
}
monitor.start(queue: DispatchQueue.global())

// Queue operations when offline
class OfflineQueue {
    private var pendingOperations: [Operation] = []
    
    func queueOperation(_ operation: Operation) {
        if isOnline {
            execute(operation)
        } else {
            pendingOperations.append(operation)
        }
    }
    
    func syncWhenOnline() {
        for operation in pendingOperations {
            execute(operation)
        }
        pendingOperations.removeAll()
    }
}
```

## Battery Optimization

### Reduce Power Consumption
```swift
// Minimize location updates
locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
locationManager.distanceFilter = 100  // Meters

// Pause location updates when not needed
locationManager.pausesLocationUpdatesAutomatically = true
locationManager.allowsBackgroundLocationUpdates = false

// Reduce motion updates
motionManager.accelerometerUpdateInterval = 1.0  // Not 0.01

// Batch network requests
// Avoid frequent small requests
// Combine multiple requests into one
```

### Background Tasks
```swift
// Use BGTaskScheduler for efficient background work
import BackgroundTasks

// Register task
BGTaskScheduler.shared.register(
    forTaskWithIdentifier: "com.app.refresh",
    using: nil
) { task in
    handleRefresh(task: task as! BGAppRefreshTask)
}

// Schedule task
let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)  // 15 minutes
try BGTaskScheduler.shared.submit(request)

// Handle task
func handleRefresh(task: BGAppRefreshTask) {
    let operation = RefreshOperation()
    
    task.expirationHandler = {
        operation.cancel()
    }
    
    operation.completionBlock = {
        task.setTaskCompleted(success: !operation.isCancelled)
        scheduleNextRefresh()
    }
    
    operationQueue.addOperation(operation)
}
```

## Database Performance

### Core Data Optimization
```swift
// Use batch operations
let batchDelete = NSBatchDeleteRequest(fetchRequest: fetchRequest)
try context.execute(batchDelete)

let batchUpdate = NSBatchUpdateRequest(entity: entity)
batchUpdate.propertiesToUpdate = ["status": "active"]
batchUpdate.predicate = predicate
try context.execute(batchUpdate)

// Fetch only needed properties
fetchRequest.propertiesToFetch = ["name", "email"]
fetchRequest.resultType = .dictionaryResultType

// Use faulting efficiently
fetchRequest.returnsObjectsAsFaults = true  // Default, load on demand
fetchRequest.relationshipKeyPathsForPrefetching = ["posts"]  // Prefetch relationships

// Index frequently queried attributes
// In Core Data model: Select attribute > Data Model Inspector > Indexed: Yes
```

### SwiftData Optimization
```swift
// Efficient queries
@Query(
    filter: #Predicate<User> { $0.age > 18 },
    sort: \.name,
    animation: .default
) var users: [User]

// Batch operations
modelContext.insert(users)
try modelContext.save()

// Background context for heavy operations
let backgroundContext = ModelContext(modelContainer)
Task.detached {
    // Perform heavy work on background context
    try backgroundContext.save()
}
```

## Testing & Profiling

### Instruments
```swift
// Time Profiler - CPU usage
// Allocations - Memory usage
// Leaks - Memory leaks
// Network - Network activity
// Energy Log - Battery impact
// Animation Hitches - UI stuttering

// Use signposts for custom instrumentation
import os.signpost

let log = OSLog(subsystem: "com.app", category: .pointsOfInterest)
os_signpost(.begin, log: log, name: "Heavy Operation")
performHeavyOperation()
os_signpost(.end, log: log, name: "Heavy Operation")
```

### XCTest Performance
```swift
func testSearchPerformance() {
    let viewModel = ViewModel()
    
    measure {
        viewModel.search(query: "test")
    }
}

// Set baseline for regression detection
// Product > Perform Action > Set Baseline
```

### MetricKit
```swift
import MetricKit

class MetricsManager: NSObject, MXMetricManagerSubscriber {
    override init() {
        super.init()
        MXMetricManager.shared.add(self)
    }
    
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            // Analyze metrics
            let cpuMetrics = payload.cpuMetrics
            let memoryMetrics = payload.memoryMetrics
            let displayMetrics = payload.displayMetrics
            
            // Send to analytics
        }
    }
}
```

## Best Practices

### General Guidelines
1. Profile before optimizing - measure, don't guess
2. Optimize for the common case, not edge cases
3. Use lazy evaluation where appropriate
4. Prefer value types (structs) over reference types (classes)
5. Minimize work on the main thread
6. Cache expensive computations
7. Use appropriate data structures
8. Release resources when not needed
9. Test on actual devices, not just simulators
10. Monitor production performance with MetricKit

### Optimization Checklist
- [ ] App launches in < 400ms (Time Profiler)
- [ ] No memory leaks (Leaks instrument)
- [ ] Memory usage stable during normal use (Allocations)
- [ ] UI responsive at 60fps (Animation Hitches)
- [ ] Network requests minimized and cached
- [ ] Images downsampled to display size
- [ ] Long lists use lazy loading
- [ ] Heavy work off main thread
- [ ] Background tasks use BGTaskScheduler
- [ ] Database queries optimized with indexes
