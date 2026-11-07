// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "SGAProtection", platforms: [.iOS(.v15), .macOS(.v13)], products: [.library(name: "SGAProtection", targets: ["SGAProtection"])], targets: [.target(name: "SGAProtection"), .testTarget(name: "SGAProtectionTests", dependencies: ["SGAProtection"])])
