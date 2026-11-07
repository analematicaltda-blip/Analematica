// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "SGAVault", platforms: [.iOS(.v15), .macOS(.v13)], products: [.library(name: "SGAVault", targets: ["SGAVault"])], targets: [.target(name: "SGAVault"), .testTarget(name: "SGAVaultTests", dependencies: ["SGAVault"])])
