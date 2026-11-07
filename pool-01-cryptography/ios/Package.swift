// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "SGAVault", platforms: [.iOS(.v15), .macOS(.v13)], products: [.library(name: "SGAVault", targets: ["SGAVault"])], dependencies: [.package(name: "SGAIntegrity", path: "../../pool-03-integrity/ios")], targets: [.target(name: "SGAVault", dependencies: [.product(name: "SGAIntegrity", package: "SGAIntegrity")]), .testTarget(name: "SGAVaultTests", dependencies: ["SGAVault"])])
