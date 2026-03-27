# Apple Frameworks Reference

## Foundation

### Core Data Types
```swift
// Strings
let string = "Hello"
let substring = string[string.startIndex..<string.index(string.startIndex, offsetBy: 5)]
let nsString = string as NSString  // Bridge to Objective-C

// Numbers
let int: Int = 42
let double: Double = 3.14
let decimal = Decimal(string: "19.99")  // Precise decimal arithmetic

// Dates
let now = Date()
let calendar = Calendar.current
let components = calendar.dateComponents([.year, .month, .day], from: now)
let formatter = DateFormatter()
formatter.dateStyle = .medium
```

### Collections
```swift
// Array operations
var array = [1, 2, 3]
array.append(4)
array.insert(0, at: 0)
let filtered = array.filter { $0 > 1 }

// Dictionary
var dict = ["key": "value"]
dict["newKey"] = "newValue"
let value = dict["key"] ?? "default"

// Set
var set: Set = [1, 2, 3]
set.insert(4)
let intersection = set.intersection([2, 3, 4])
```

### FileManager
```swift
let fileManager = FileManager.default

// Directories
let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first
let fileURL = documentsURL?.appendingPathComponent("data.json")

// File operations
if fileManager.fileExists(atPath: fileURL?.path ?? "") {
    try fileManager.removeItem(at: fileURL!)
}

try data.write(to: fileURL!)
let contents = try Data(contentsOf: fileURL!)

// Directory enumeration
let enumerator = fileManager.enumerator(at: documentsURL!, includingPropertiesForKeys: nil)
while let file = enumerator?.nextObject() as? URL {
    print(file.lastPathComponent)
}
```

### UserDefaults
```swift
let defaults = UserDefaults.standard

// Save
defaults.set("value", forKey: "key")
defaults.set(42, forKey: "count")
defaults.set(true, forKey: "isEnabled")

// Retrieve
let value = defaults.string(forKey: "key")
let count = defaults.integer(forKey: "count")
let isEnabled = defaults.bool(forKey: "isEnabled")

// Remove
defaults.removeObject(forKey: "key")

// Observe changes
defaults.addObserver(self, forKeyPath: "key", options: .new, context: nil)
```

## UIKit (iOS)

### View Controllers
```swift
class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        refreshData()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        startAnimations()
    }
}

// Navigation
let vc = DetailViewController()
navigationController?.pushViewController(vc, animated: true)
navigationController?.popViewController(animated: true)

// Modal presentation
present(vc, animated: true)
dismiss(animated: true)
```

### Table Views
```swift
class TableViewController: UITableViewController {
    override func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return items.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        cell.textLabel?.text = items[indexPath.row].name
        return cell
    }
    
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        showDetail(for: items[indexPath.row])
    }
}
```

### Auto Layout
```swift
// Programmatic constraints
view.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    view.topAnchor.constraint(equalTo: superview.topAnchor, constant: 20),
    view.leadingAnchor.constraint(equalTo: superview.leadingAnchor, constant: 16),
    view.trailingAnchor.constraint(equalTo: superview.trailingAnchor, constant: -16),
    view.heightAnchor.constraint(equalToConstant: 44)
])

// Layout guides
view.topAnchor.constraint(equalTo: safeAreaLayoutGuide.topAnchor)
view.bottomAnchor.constraint(equalTo: safeAreaLayoutGuide.bottomAnchor)
```

## AppKit (macOS)

### NSViewController
```swift
class ViewController: NSViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    override func viewWillAppear() {
        super.viewWillAppear()
        refreshData()
    }
}
```

### NSWindow
```swift
let window = NSWindow(
    contentRect: NSRect(x: 0, y: 0, width: 800, height: 600),
    styleMask: [.titled, .closable, .miniaturizable, .resizable],
    backing: .buffered,
    defer: false
)
window.title = "My App"
window.center()
window.makeKeyAndOrderFront(nil)
```

### NSMenu
```swift
let menu = NSMenu()
let item = NSMenuItem(title: "Action", action: #selector(performAction), keyEquivalent: "a")
menu.addItem(item)
NSApp.mainMenu?.addItem(menuItem)
```

## Networking

### URLSession
```swift
// Simple GET request
let url = URL(string: "https://api.example.com/data")!
let (data, response) = try await URLSession.shared.data(from: url)

// POST request
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
request.httpBody = try JSONEncoder().encode(userData)

let (data, response) = try await URLSession.shared.data(for: request)

// Download task
let (fileURL, response) = try await URLSession.shared.download(from: url)

// Upload task
let (data, response) = try await URLSession.shared.upload(for: request, from: fileData)

// Custom configuration
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 30
config.waitsForConnectivity = true
let session = URLSession(configuration: config)
```

### Codable
```swift
struct User: Codable {
    let id: Int
    let name: String
    let email: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case name = "full_name"
        case email = "email_address"
    }
}

// Decode
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
let user = try decoder.decode(User.self, from: jsonData)

// Encode
let encoder = JSONEncoder()
encoder.keyEncodingStrategy = .convertToSnakeCase
let jsonData = try encoder.encode(user)
```

## Core Data

### Stack Setup
```swift
lazy var persistentContainer: NSPersistentContainer = {
    let container = NSPersistentContainer(name: "Model")
    container.loadPersistentStores { description, error in
        if let error = error {
            fatalError("Unable to load persistent stores: \(error)")
        }
    }
    return container
}()

var context: NSManagedObjectContext {
    persistentContainer.viewContext
}
```

### CRUD Operations
```swift
// Create
let user = User(context: context)
user.name = "John"
user.email = "john@example.com"
try context.save()

// Read
let fetchRequest: NSFetchRequest<User> = User.fetchRequest()
fetchRequest.predicate = NSPredicate(format: "name == %@", "John")
fetchRequest.sortDescriptors = [NSSortDescriptor(key: "name", ascending: true)]
let users = try context.fetch(fetchRequest)

// Update
if let user = users.first {
    user.name = "Jane"
    try context.save()
}

// Delete
if let user = users.first {
    context.delete(user)
    try context.save()
}
```

### Fetch Request
```swift
let fetchRequest: NSFetchRequest<User> = User.fetchRequest()

// Predicates
fetchRequest.predicate = NSPredicate(format: "age > %d", 18)
fetchRequest.predicate = NSPredicate(format: "name CONTAINS[cd] %@", "john")
fetchRequest.predicate = NSPredicate(format: "email ENDSWITH %@", "@example.com")

// Sort
fetchRequest.sortDescriptors = [
    NSSortDescriptor(key: "lastName", ascending: true),
    NSSortDescriptor(key: "firstName", ascending: true)
]

// Limit
fetchRequest.fetchLimit = 20
fetchRequest.fetchOffset = 40  // Pagination
```

## SwiftData (iOS 17+)

### Model Definition
```swift
@Model
class User {
    @Attribute(.unique) var id: UUID
    var name: String
    var email: String
    @Relationship(deleteRule: .cascade) var posts: [Post]
    
    init(name: String, email: String) {
        self.id = UUID()
        self.name = name
        self.email = email
    }
}
```

### Container Setup
```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [User.self, Post.self])
    }
}
```

### Queries
```swift
@Query var users: [User]
@Query(sort: \.name) var sortedUsers: [User]
@Query(filter: #Predicate<User> { $0.age > 18 }) var adults: [User]
```

## Combine

### Publishers
```swift
// Just - single value
Just("Hello").sink { print($0) }

// Future - async single value
Future { promise in
    DispatchQueue.global().async {
        promise(.success("Result"))
    }
}

// PassthroughSubject - emit values manually
let subject = PassthroughSubject<String, Never>()
subject.send("Value 1")
subject.send("Value 2")
subject.send(completion: .finished)

// CurrentValueSubject - subject with initial value
let currentSubject = CurrentValueSubject<Int, Never>(0)
print(currentSubject.value)  // 0
currentSubject.send(1)
```

### Operators
```swift
publisher
    .map { $0.uppercased() }
    .filter { $0.count > 3 }
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .flatMap { value in
        fetchData(for: value)
    }
    .catch { error in
        Just("Default")
    }
    .sink { completion in
        print("Completed: \(completion)")
    } receiveValue: { value in
        print("Received: \(value)")
    }
    .store(in: &cancellables)
```

### Combine with SwiftUI
```swift
class ViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var results: [String] = []
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        $searchText
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .sink { [weak self] text in
                self?.performSearch(text)
            }
            .store(in: &cancellables)
    }
}
```

## CloudKit

### Setup
```swift
let container = CKContainer.default()
let publicDatabase = container.publicCloudDatabase
let privateDatabase = container.privateCloudDatabase
```

### CRUD Operations
```swift
// Create record
let record = CKRecord(recordType: "User")
record["name"] = "John"
record["email"] = "john@example.com"

try await publicDatabase.save(record)

// Fetch record
let recordID = CKRecord.ID(recordName: "unique-id")
let fetchedRecord = try await publicDatabase.record(for: recordID)

// Query records
let predicate = NSPredicate(format: "name == %@", "John")
let query = CKQuery(recordType: "User", predicate: predicate)
let (results, _) = try await publicDatabase.records(matching: query)

// Delete record
try await publicDatabase.deleteRecord(withID: recordID)
```

## StoreKit

### In-App Purchase
```swift
// Fetch products
let productIDs: Set<String> = ["com.app.premium"]
let products = try await Product.products(for: productIDs)

// Purchase
if let product = products.first {
    let result = try await product.purchase()
    
    switch result {
    case .success(let verification):
        let transaction = try verification.payloadValue
        await transaction.finish()
        
    case .userCancelled:
        print("User cancelled")
        
    case .pending:
        print("Purchase pending")
        
    @unknown default:
        break
    }
}

// Restore purchases
for await result in Transaction.currentEntitlements {
    let transaction = try result.payloadValue
    // Grant access based on transaction
}
```

## AVFoundation

### Audio Playback
```swift
import AVFoundation

let url = Bundle.main.url(forResource: "sound", withExtension: "mp3")!
let player = try AVAudioPlayer(contentsOf: url)
player.play()
player.pause()
player.stop()
```

### Video Playback
```swift
import AVKit

let url = URL(string: "https://example.com/video.mp4")!
let player = AVPlayer(url: url)
let playerViewController = AVPlayerViewController()
playerViewController.player = player
present(playerViewController, animated: true) {
    player.play()
}
```

### Camera Capture
```swift
import AVFoundation

let session = AVCaptureSession()
session.sessionPreset = .photo

guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) else { return }
let input = try AVCaptureDeviceInput(device: device)
session.addInput(input)

let output = AVCapturePhotoOutput()
session.addOutput(output)

session.startRunning()

// Capture photo
let settings = AVCapturePhotoSettings()
output.capturePhoto(with: settings, delegate: self)
```

## Core Location

### Location Manager
```swift
import CoreLocation

class LocationManager: NSObject, CLLocationManagerDelegate {
    let manager = CLLocationManager()
    
    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }
    
    func requestLocation() {
        manager.requestWhenInUseAuthorization()
        manager.requestLocation()
    }
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        if let location = locations.first {
            print("Location: \(location.coordinate)")
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Error: \(error.localizedDescription)")
    }
}
```

## MapKit

### Map View
```swift
import MapKit

struct MapView: View {
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )
    
    var body: some View {
        Map(coordinateRegion: $region, annotationItems: locations) { location in
            MapMarker(coordinate: location.coordinate, tint: .red)
        }
    }
}
```

## HealthKit

### Authorization & Queries
```swift
import HealthKit

let healthStore = HKHealthStore()

// Request authorization
let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount)!
let types = Set([stepType])

healthStore.requestAuthorization(toShare: types, read: types) { success, error in
    if success {
        print("Authorized")
    }
}

// Query step count
let predicate = HKQuery.predicateForSamples(withStart: Date().addingTimeInterval(-86400), end: Date())
let query = HKStatisticsQuery(quantityType: stepType, quantitySamplePredicate: predicate, options: .cumulativeSum) { query, result, error in
    if let sum = result?.sumQuantity() {
        let steps = sum.doubleValue(for: HKUnit.count())
        print("Steps: \(steps)")
    }
}

healthStore.execute(query)
```

## Core Animation

### Basic Animations
```swift
// UIView animations
UIView.animate(withDuration: 0.3) {
    view.alpha = 0
    view.transform = CGAffineTransform(scaleX: 1.5, y: 1.5)
}

// CALayer animations
let animation = CABasicAnimation(keyPath: "position")
animation.fromValue = layer.position
animation.toValue = CGPoint(x: 200, y: 200)
animation.duration = 1.0
layer.add(animation, forKey: "position")
```

## Observation (iOS 17+)

### Observable Objects
```swift
@Observable
class DataModel {
    var items: [Item] = []
    var isLoading = false
    
    func refresh() async {
        isLoading = true
        items = await fetchItems()
        isLoading = false
    }
}

// In SwiftUI - automatically observes changes
struct ContentView: View {
    let model = DataModel()
    
    var body: some View {
        List(model.items) { item in
            Text(item.name)
        }
    }
}
```
