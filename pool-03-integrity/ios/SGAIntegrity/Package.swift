// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "SGAIntegrity", platforms: [.iOS(.v15), .macOS(.v13)], products: [.library(name: "SGAIntegrity", targets: ["SGAIntegrity"])], targets: [.target(name: "SGAIntegrity"), .testTarget(name: "SGAIntegrityTests", dependencies: ["SGAIntegrity"])])
