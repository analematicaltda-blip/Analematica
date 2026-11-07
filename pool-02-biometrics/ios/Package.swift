// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "SGAApproval", platforms: [.iOS(.v15), .macOS(.v13)], products: [.library(name: "SGAApproval", targets: ["SGAApproval"])], dependencies: [.package(name: "SGAIntegrity", path: "../../pool-03-integrity/ios")], targets: [.target(name: "SGAApproval", dependencies: [.product(name: "SGAIntegrity", package: "SGAIntegrity")]), .testTarget(name: "SGAApprovalTests", dependencies: ["SGAApproval"])])
